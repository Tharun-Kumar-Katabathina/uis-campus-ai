"""Retrieval + generation-reliability evaluation over the sample corpus.
See evaluation/README.md and docs/PROJECT_CONTRACT.md Module 6 for the
methodology and why generation quality is measured via the verification
layer rather than a live LLM call.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from app.retrieval.hybrid import hybrid_search
from app.retrieval.vector_search import FastEmbedEmbedder
from app.verification.citations import validate_citations
from app.verification.grounding import MIN_OVERLAP_RATIO, verify_answer

from evaluation import corpus, metrics

DEFAULT_DATASET = Path(__file__).resolve().parent / "datasets" / "eval_questions.json"

# A confidently-wrong sentence sharing essentially no vocabulary with any
# real evidence in evaluation/evaluation/corpus.py — used to prove
# hallucinated/off-topic content gets caught (see build_bad_answer below).
_UNRELATED_CLAIM = "The university mascot is a friendly dragon that lives near the fountain"


@dataclass
class EvalReport:
    question_count: int
    answerable_count: int
    no_answer_count: int
    recall_at_3: float
    precision_at_3: float
    mrr: float
    hit_rate: float
    faithfulness_rate: float
    citation_correctness_rate: float
    hallucination_catch_rate: float
    abstention_quality: float

    def summary(self) -> str:
        return (
            f"Questions: {self.question_count} "
            f"({self.answerable_count} answerable, {self.no_answer_count} no-answer)\n"
            f"Retrieval:\n"
            f"  Recall@3:    {self.recall_at_3:.3f}\n"
            f"  Precision@3: {self.precision_at_3:.3f}\n"
            f"  MRR:         {self.mrr:.3f}\n"
            f"  Hit Rate:    {self.hit_rate:.3f}\n"
            f"Generation reliability (via verification layer):\n"
            f"  Faithfulness rate:         {self.faithfulness_rate:.3f}\n"
            f"  Citation correctness rate: {self.citation_correctness_rate:.3f}\n"
            f"  Hallucination catch rate:  {self.hallucination_catch_rate:.3f}\n"
            f"  Abstention quality:        {self.abstention_quality:.3f}\n"
        )


def load_dataset(path: Path = DEFAULT_DATASET) -> list[dict]:
    return json.loads(path.read_text())


def build_good_answer(evidence_index: int, evidence_content: str) -> str:
    """A well-formed answer: cites real evidence, and is drawn directly
    from that evidence's own content, so it should pass verification."""
    first_sentence = evidence_content.split(".")[0].strip()
    return f"{first_sentence} [{evidence_index}]."


def build_bad_answer(evidence_index: int) -> str:
    """Cites a real evidence index (so citation validation alone can't
    catch it) but states a claim with no lexical connection to that
    evidence's actual content — should fail the grounding check."""
    return f"{_UNRELATED_CLAIM} [{evidence_index}]."


def run(dataset_path: Path = DEFAULT_DATASET) -> EvalReport:
    embedder = FastEmbedEmbedder()
    client, keyword_index = corpus.seed(embedder)
    dataset = load_dataset(dataset_path)

    retrieval_pairs: list[tuple[list[str], str]] = []
    faithful, cited_ok, caught_hallucination, abstained = [], [], [], []

    for item in dataset:
        results = hybrid_search(
            item["question"], top_k=3, keyword_index=keyword_index, embedder=embedder, client=client
        )
        retrieved_ids = [r.document_id for r in results]

        if not item["expect_no_answer"]:
            retrieval_pairs.append((retrieved_ids, item["expected_document_id"]))

            if results:
                good = build_good_answer(1, results[0].content)
                faithful.append(verify_answer(good, results))
                cited_ok.append(validate_citations(good, results))

                bad = build_bad_answer(1)
                caught_hallucination.append(not verify_answer(bad, results))
        else:
            if not results:
                abstained.append(True)
            else:
                confidently_wrong = build_bad_answer(1)
                abstained.append(not verify_answer(confidently_wrong, results))

    return EvalReport(
        question_count=len(dataset),
        answerable_count=len(retrieval_pairs),
        no_answer_count=len(dataset) - len(retrieval_pairs),
        recall_at_3=metrics.recall_at_k(retrieval_pairs),
        precision_at_3=metrics.precision_at_k(retrieval_pairs, k=3),
        mrr=metrics.mean_reciprocal_rank(retrieval_pairs),
        hit_rate=metrics.hit_rate(retrieval_pairs),
        faithfulness_rate=sum(faithful) / len(faithful) if faithful else 0.0,
        citation_correctness_rate=sum(cited_ok) / len(cited_ok) if cited_ok else 0.0,
        hallucination_catch_rate=(
            sum(caught_hallucination) / len(caught_hallucination) if caught_hallucination else 0.0
        ),
        abstention_quality=sum(abstained) / len(abstained) if abstained else 0.0,
    )


def main() -> None:
    report = run()
    print(f"(grounding lexical-overlap floor: {MIN_OVERLAP_RATIO})")
    print(report.summary())


if __name__ == "__main__":
    main()
