Analyze the following content items collected over the past {time_range} and identify trending topics.

For each trend, provide:
- **Topic**: [Short name]
- **Description**: [1-2 sentences on what's happening]
- **Sentiment**: [Score from -1.0 to 1.0, negative = critical, positive = optimistic]
- **Momentum**: [Score from 0.0 to 1.0, 0 = fading, 1 = accelerating]
- **Related content IDs**: [List of content IDs that relate to this trend]

Return as a JSON array of objects with keys: topic, description, sentiment_score, momentum_score, related_content_ids.

Content items (each prefixed with [ID]):
{content}
