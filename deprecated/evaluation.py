import numpy as np
from collections import defaultdict

from train_cf import load_data, train, SAMPLE_SIZE


RELEVANCE_THRESHOLD = 4.0


def _get_top_n(predictions, n=10):
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est, true_r))
    for uid in top_n:
        top_n[uid].sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = top_n[uid][:n]
    return top_n


def precision_at_k(predictions, k=10, threshold=RELEVANCE_THRESHOLD):
    top_n = _get_top_n(predictions, n=k)
    precisions = []
    for uid, user_ratings in top_n.items():
        relevant = sum(1 for _, est, _ in user_ratings if est >= threshold)
        precisions.append(relevant / k)
    return np.mean(precisions)


def recall_at_k(predictions, k=10, threshold=RELEVANCE_THRESHOLD):
    top_n = _get_top_n(predictions, n=k)

    all_relevant = defaultdict(int)
    for uid, iid, true_r, est, _ in predictions:
        if true_r >= threshold:
            all_relevant[uid] += 1

    recalls = []
    for uid, user_ratings in top_n.items():
        relevant_in_top_k = sum(1 for _, est, _ in user_ratings if est >= threshold)
        total_relevant = all_relevant.get(uid, 0)
        if total_relevant > 0:
            recalls.append(relevant_in_top_k / total_relevant)
    return np.mean(recalls) if recalls else 0.0


def dcg_at_k(relevances, k):
    relevances = np.array(relevances[:k])
    if relevances.size == 0:
        return 0.0
    return np.sum(relevances / np.log2(np.arange(2, relevances.size + 2)))


def ndcg_at_k(predictions, k=10, threshold=RELEVANCE_THRESHOLD):
    top_n = _get_top_n(predictions, n=k)

    user_true_relevant = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        user_true_relevant[uid].append(true_r)

    ndcgs = []
    for uid, user_ratings in top_n.items():
        relevances = [1.0 if est >= threshold else 0.0 for _, est, _ in user_ratings]
        dcg = dcg_at_k(relevances, k)

        all_scores = sorted(user_true_relevant[uid], reverse=True)
        ideal_relevances = [1.0 if r >= threshold else 0.0 for r in all_scores[:k]]
        idcg = dcg_at_k(ideal_relevances, k)

        ndcgs.append(dcg / idcg if idcg > 0 else 0.0)
    return np.mean(ndcgs) if ndcgs else 0.0


def evaluate(predictions, k=10):
    p = precision_at_k(predictions, k=k)
    r = recall_at_k(predictions, k=k)
    n = ndcg_at_k(predictions, k=k)
    return {"precision@k": p, "recall@k": r, "ndcg@k": n}


if __name__ == "__main__":
    print("Loading data and training model for evaluation...")
    sample = SAMPLE_SIZE if SAMPLE_SIZE > 0 else None
    data, _ = load_data(sample_size=sample)
    _, _, _, predictions, rmse = train(data)

    k = 10
    metrics = evaluate(predictions, k=k)
    print(f"\n{'='*40}")
    print(f"  Evaluation Metrics (K={k})")
    print(f"{'='*40}")
    print(f"  RMSE:         {rmse:.4f}")
    print(f"  Precision@{k}: {metrics['precision@k']:.4f}")
    print(f"  Recall@{k}:    {metrics['recall@k']:.4f}")
    print(f"  NDCG@{k}:      {metrics['ndcg@k']:.4f}")
    print(f"{'='*40}")
