from flask import Flask, request, render_template
from dotenv import load_dotenv
from openai import OpenAI
import os

app = Flask(__name__)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# 감정 매핑 데이터
emotion_data = {
    "기쁨": {
        "emoticons": ["😄", "🎉", "✨"],
        "gif_keywords": ["happy", "celebration", "smile"],
        "reactions": {
            "empathetic": ["정말 기뻐 보여요!", "당신의 행복이 전해지네요!"],
            "humorous": ["행복 바이러스 전염 중 😂", "웃음 주의보 발령!"],
            "practical": ["이 기쁨을 오래 간직하세요.", "행복한 순간을 기록해두세요."]
        },
        "suggestion": "좋은 기분을 친구와 나누세요.",
        "tags": ["positive", "energy", "fun"]
    },
    "슬픔": {
        "emoticons": ["😢", "💔", "🌧"],
        "gif_keywords": ["sad", "crying", "alone"],
        "reactions": {
            "empathetic": ["힘든 시간을 보내고 있군요.", "마음이 아프겠어요."],
            "humorous": ["눈물도 이모지로는 귀엽네요 😭", "울다가 웃으면 코로 바람 나와요 🤧"],
            "practical": ["잠시 휴식을 가져보세요.", "마음을 털어놓을 사람을 찾아보세요."]
        },
        "suggestion": "감정을 억누르지 말고 표현하세요.",
        "tags": ["negative", "low", "comfort"]
    },
    "분노": {
        "emoticons": ["😡", "🔥", "💢"],
        "gif_keywords": ["angry", "rage", "frustrated"],
        "reactions": {
            "empathetic": ["화가 날 만한 상황이군요.", "당연히 속상할 수 있어요."],
            "humorous": ["불타오르네 🔥", "화내면 주름 생겨요 😅"],
            "practical": ["잠시 호흡을 가다듬어보세요.", "산책을 하면서 진정해보세요."]
        },
        "suggestion": "감정을 글로 적어보며 정리하세요.",
        "tags": ["negative", "anger", "stress"]
    },
    "놀람": {
        "emoticons": ["😲", "😮", "🙀"],
        "gif_keywords": ["shocked", "surprised", "wow"],
        "reactions": {
            "empathetic": ["정말 놀라운 일이네요!", "충분히 놀랄 만해요."],
            "humorous": ["깜놀 😂", "심장이 쿵쾅!"],
            "practical": ["상황을 천천히 다시 살펴보세요.", "주변 사람에게 이야기해보세요."]
        },
        "suggestion": "놀란 마음을 진정시켜보세요.",
        "tags": ["neutral", "unexpected", "event"]
    },
    "두려움": {
        "emoticons": ["😨", "😱", "👻"],
        "gif_keywords": ["scary", "fear", "horror"],
        "reactions": {
            "empathetic": ["무서울 수 있어요.", "그 마음 이해해요."],
            "humorous": ["귀신보다 무서운 건 월급날 통장 😅", "으악! 저도 깜짝 놀랐어요."],
            "practical": ["안전한 환경에 있는지 확인하세요.", "믿을 만한 사람과 함께 하세요."]
        },
        "suggestion": "호흡을 깊게 하며 긴장을 풀어보세요.",
        "tags": ["negative", "anxiety", "fear"]
    },
    "피곤함": {
        "emoticons": ["😴", "🥱", "💤"],
        "gif_keywords": ["tired", "sleep", "rest"],
        "reactions": {
            "empathetic": ["많이 지쳤군요.", "고생이 많았어요."],
            "humorous": ["잠이 보약입니다 😴", "좀비 모드 발동 🧟"],
            "practical": ["잠시 눈을 붙이세요.", "물을 마시고 스트레칭 하세요."]
        },
        "suggestion": "충분한 휴식을 취하세요.",
        "tags": ["negative", "low", "rest"]
    },
    "설렘": {
        "emoticons": ["😍", "💖", "🌸"],
        "gif_keywords": ["love", "excited", "romantic"],
        "reactions": {
            "empathetic": ["두근거리는 마음이 전해져요!", "정말 좋은 일이 있군요."],
            "humorous": ["심장이 쿵쾅쿵쾅 💓", "설렘주의보 발령!"],
            "practical": ["기대를 즐기세요.", "차분하게 마음을 다스려보세요."]
        },
        "suggestion": "설레는 기분을 글로 기록해두세요.",
        "tags": ["positive", "anticipation", "love"]
    },
    "혼란": {
        "emoticons": ["😕", "🤯", "❓"],
        "gif_keywords": ["confused", "lost", "thinking"],
        "reactions": {
            "empathetic": ["혼란스러울 만해요.", "이해가 잘 안 될 수 있죠."],
            "humorous": ["머리 위에 물음표 100개 ❓❓❓", "저도 같이 멍해지네요 😵"],
            "practical": ["정보를 하나씩 정리해보세요.", "주변에 물어보는 것도 좋아요."]
        },
        "suggestion": "정리된 노트를 작성해보세요.",
        "tags": ["neutral", "thinking", "uncertainty"]
    },
    "자신감": {
        "emoticons": ["💪", "😎", "🔥"],
        "gif_keywords": ["confident", "success", "win"],
        "reactions": {
            "empathetic": ["정말 멋져요!", "당신의 자신감이 돋보여요."],
            "humorous": ["자신감 뿜뿜 💥", "이건 거의 주인공 포스 😎"],
            "practical": ["그 에너지를 잘 활용하세요.", "지금의 기운으로 도전해보세요."]
        },
        "suggestion": "자신감을 행동으로 옮겨보세요.",
        "tags": ["positive", "power", "success"]
    }
}

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        user_input = request.form["user_input"]

        # OpenAI API 호출
        completion = client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": "너는 감정 분석기야. 사용자의 문장에서 가장 적절한 감정을 추출해. (기쁨, 슬픔, 분노, 놀람, 두려움, 피곤함, 설렘, 혼란, 자신감 중 하나로 답해)"},
                {"role": "user", "content": user_input}
            ]
        )
        detected_emotion = completion.choices[0].message.content.strip()

        if detected_emotion in emotion_data:
            result = emotion_data[detected_emotion]
            result["emotion"] = detected_emotion
        else:
            result = {
                "emotion": "알 수 없음",
                "emoticons": ["❓"],
                "reactions": {"empathetic": [], "humorous": [], "practical": []},
                "suggestion": "분류되지 않았습니다.",
                "tags": []
            }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
