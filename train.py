"""One-command training: fine-tune Sentence-BERT and auto-save the model.

Run it once (heavy dataset), it saves the checkpoint, then the backend just loads it.

    python train.py                      # default: QQP (364k pairs), auto-downloaded
    python train.py --dataset mrpc       # smaller/faster paraphrase set
    python train.py --dataset csv --data notebooks/data/mit.csv   # your Kaggle CSV
    python train.py --sample 30000 --epochs 1                     # quick MVP run

The default dataset (QQP) is pulled from HuggingFace automatically -- no Kaggle login
needed -- so this command works out of the box.
"""
from __future__ import annotations

import argparse
import os

import torch

# Where the backend expects the fine-tuned model.
DEFAULT_OUT = os.path.join('backend', 'detector', 'models', 'plagiarism-sbert')


def load_pairs(dataset: str, data_path: str | None):
    """Return three lists: text_a, text_b, label(0/1)."""
    if dataset == 'csv':
        import pandas as pd

        if not data_path or not os.path.exists(data_path):
            raise SystemExit(f'--data CSV not found: {data_path}')
        sep = '\t' if data_path.endswith(('.txt', '.tsv')) else ','
        df = pd.read_csv(data_path, sep=sep)
        df.columns = [c.lower() for c in df.columns]
        text_cols = [c for c in df.columns
                     if any(k in c for k in ('sentence', 'text', 'source', 'target', 'question'))]
        label_col = next((c for c in df.columns
                          if any(k in c for k in ('label', 'plag', 'similar', 'is_dup'))),
                         df.columns[-1])
        df = df[[text_cols[0], text_cols[1], label_col]].dropna()
        return (df.iloc[:, 0].tolist(), df.iloc[:, 1].tolist(),
                df.iloc[:, 2].astype(int).tolist())

    # HuggingFace datasets -- downloaded automatically, no auth.
    from datasets import load_dataset

    # Namespaced repo ids (required by recent huggingface_hub).
    if dataset == 'qqp':
        ds = load_dataset('nyu-mll/glue', 'qqp', split='train')
        return ds['question1'], ds['question2'], ds['label']
    if dataset == 'mrpc':
        ds = load_dataset('nyu-mll/glue', 'mrpc', split='train')
        return ds['sentence1'], ds['sentence2'], ds['label']
    if dataset == 'paws':
        ds = load_dataset('google-research-datasets/paws', 'labeled_final', split='train')
        return ds['sentence1'], ds['sentence2'], ds['label']
    raise SystemExit(f'Unknown dataset: {dataset}')


def main():
    ap = argparse.ArgumentParser(description='Fine-tune Sentence-BERT for plagiarism detection.')
    ap.add_argument('--dataset', default='qqp', choices=['qqp', 'mrpc', 'paws', 'csv'])
    ap.add_argument('--data', default=None, help='CSV path when --dataset csv')
    ap.add_argument('--sample', type=int, default=30000,
                    help='max training pairs (0 = use all). Keep small for a fast MVP run.')
    ap.add_argument('--epochs', type=int, default=1)
    ap.add_argument('--batch', type=int, default=32)
    ap.add_argument('--base', default='all-MiniLM-L6-v2')
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args()

    from sentence_transformers import InputExample, SentenceTransformer, losses
    from torch.utils.data import DataLoader

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Device: {device}')
    print(f'Loading dataset: {args.dataset} ...')
    text_a, text_b, labels = load_pairs(args.dataset, args.data)
    print(f'  {len(labels)} pairs loaded')

    if args.sample and len(labels) > args.sample:
        text_a = text_a[:args.sample]
        text_b = text_b[:args.sample]
        labels = labels[:args.sample]
        print(f'  using first {args.sample} pairs (--sample)')

    # Hold out 10% for a quick evaluation.
    n_eval = max(1, len(labels) // 10)
    train_examples = [
        InputExample(texts=[a, b], label=float(l))
        for a, b, l in zip(text_a[n_eval:], text_b[n_eval:], labels[n_eval:])
    ]
    eval_a, eval_b, eval_y = text_a[:n_eval], text_b[:n_eval], labels[:n_eval]

    model = SentenceTransformer(args.base, device=device)
    loader = DataLoader(train_examples, shuffle=True, batch_size=args.batch)
    loss = losses.CosineSimilarityLoss(model)

    print(f'Training {len(train_examples)} pairs for {args.epochs} epoch(s)...')
    model.fit(
        train_objectives=[(loader, loss)],
        epochs=args.epochs,
        warmup_steps=int(len(loader) * 0.1),
        show_progress_bar=True,
    )

    # Quick evaluation: cosine >= 0.7 -> predicted plagiarised.
    import numpy as np

    ea = model.encode(eval_a, convert_to_numpy=True)
    eb = model.encode(eval_b, convert_to_numpy=True)
    cos = (ea * eb).sum(1) / (np.linalg.norm(ea, axis=1) * np.linalg.norm(eb, axis=1) + 1e-8)
    pred = (cos >= 0.7).astype(int)
    y = np.array(eval_y)
    acc = float((pred == y).mean())
    print(f'Held-out accuracy @0.7 threshold: {acc:.3f}')

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    model.save(args.out)
    print(f'\n✅ Saved fine-tuned model -> {args.out}')
    print('The backend now loads this automatically (health shows model_fine_tuned: true).')


if __name__ == '__main__':
    main()
