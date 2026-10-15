from collections import defaultdict, Counter

def analyze_score_distribution(analyzed_stream):
    """
    Consumes the analyzed metadata stream, yields each item unchanged,
    and returns a formatted summary of score distributions and tag counts.
    """
    total_images = 0
    highest_score_counts = Counter()
    junk_score_dist = Counter()
    tag_counts = Counter()
    all_reasons = Counter()

    for meta in analyzed_stream:
        total_images += 1
        
        # 1. Map scores
        scores = {
            'junk': meta.get('junk score', 0),
            'symbol': meta.get('symbol score', 0),
            'art': meta.get('art score', 0),
            'character': meta.get('character score', 0)
        }
        
        # Determine highest scoring category for sorting priority
        # Default to 'unclassified' if all scores are 0
        max_score_val = max(scores.values())
        if max_score_val == 0:
            top_category = "unclassified (0 score)"
        else:
            top_category = max(scores, key=scores.get)
            
        highest_score_counts[top_category] += 1
        junk_score_dist[scores['junk']] += 1

        # 2. Count tags & reasons
        for tag in meta.get('tags', []):
            tag_counts[tag] += 1
            
        for reason in meta.get('score_reasons', []):
            all_reasons[reason] += 1

        yield meta

    # --- Print Dashboard ---
    print("\n" + "="*50)
    print(f" PIPELINE METADATA ANALYSIS SUMMARY ({total_images} Total Unique Images)")
    print("="*50)

    print("\n📊 Primary Score Classifications (Highest Score Wins):")
    for category, count in highest_score_counts.most_common():
        pct = (count / total_images) * 100 if total_images else 0
        print(f"  • {category.capitalize():<18}: {count:>4} images ({pct:>5.1f}%)")

    print("\n🗑️  Junk Score Distribution:")
    for score in sorted(junk_score_dist.keys()):
        count = junk_score_dist[score]
        print(f"  • Junk Score {score:<2}: {count:>4} images")

    print("\n🏷️  Assigned Tag Totals:")
    for tag, count in tag_counts.items():
        print(f"  • Tag '{tag}': {count:>4} images")

    print("\n🔍 Top Triggers / Reasons:")
    for reason, count in all_reasons.most_common(5):
        print(f"  • {reason:<35}: {count:>4} occurrences")
    print("="*50 + "\n")