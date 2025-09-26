from transformers import pipeline

# Use a stronger model
emotion_classifier = pipeline("text-classification",
                              model="argish/text-emotion-classifier-distilroberta",
                              return_all_scores=False)


def analyze_emotion(text: str) -> str:
    try:
        result = emotion_classifier(text)
        if result and len(result) > 0:
            label = result[0]['label'].lower()
            score = result[0]['score']
            print(f"[Emotion] {label} (confidence: {score:.2f})")
            if score >= 0.8:
                return label
            else:
                return "neutral"
        return "neutral"
    except Exception as e:
        print("[!] Emotion analysis failed:", e)
        return "error"


