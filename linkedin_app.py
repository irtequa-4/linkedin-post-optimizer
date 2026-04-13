import streamlit as st
from groq import Groq
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---- PASTE YOUR API KEY HERE ----
import os
API_KEY = os.environ.get("GROQ_API_KEY")
# ---- SCORING FUNCTION ----
def score_post(text):
    score = 0
    reasons = []

    # Length check
    words = len(text.split())
    if words >= 50:
        score += 20
    elif words >= 20:
        score += 10
        reasons.append("Too short — longer posts get more reach")
    else:
        reasons.append("Way too short — add more detail and story")

    # Hashtag check
    hashtags = text.count("#")
    if hashtags >= 3:
        score += 20
    elif hashtags >= 1:
        score += 10
        reasons.append("Add more hashtags (aim for 3–5)")
    else:
        reasons.append("No hashtags — hashtags boost visibility a lot")

    # Emoji check
    import re
    emojis = re.findall(r'[^\w\s,.]', text)
    if len(emojis) >= 2:
        score += 15
    elif len(emojis) == 1:
        score += 7
        reasons.append("Add more emojis to grab attention")
    else:
        reasons.append("No emojis — they make posts more human and clickable")

    # Readability check
    ease = textstat.flesch_reading_ease(text)
    if ease >= 60:
        score += 20
    elif ease >= 40:
        score += 10
        reasons.append("Hard to read — use shorter sentences")
    else:
        reasons.append("Very hard to read — simplify your language")

    # Emotion/sentiment check
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)
    compound = sentiment['compound']
    if compound >= 0.5 or compound <= -0.3:
        score += 25
    elif compound >= 0.2:
        score += 12
        reasons.append("Low emotion — add more feeling or personal story")
    else:
        reasons.append("Flat tone — LinkedIn loves emotion and vulnerability")

    if not reasons:
        reasons.append("Great post structure!")

    return min(score, 100), reasons


# ---- AI OPTIMIZER FUNCTION ----
def optimize_post(text):
    client = Groq(api_key=API_KEY)
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""You are a LinkedIn content expert. 
Rewrite the following post to make it more engaging, emotional, professional, and likely to go viral on LinkedIn.

Rules:
- Add a strong hook at the start
- Use short paragraphs (1-2 lines each)
- Use maximum 1-2 emojis only, or none at all if the tone is serious
- Add 3-5 relevant hashtags at the end
- Make it feel personal and human
- Keep the core message the same
- Keep the total post under 150 words maximum

Original post:
{text}

Return ONLY the rewritten post, nothing else."""
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

# ---- STREAMLIT UI ----
st.set_page_config(page_title="LinkedIn Post Optimizer", page_icon="💼")

st.title("💼 LinkedIn Post Optimizer")
st.subheader("Turn your boring post into a viral one — powered by AI")

st.markdown("---")

user_post = st.text_area("📝 Paste your LinkedIn post here:", height=200, placeholder='e.g. "I got a new job today at Google"')

if st.button("🚀 Optimize My Post!"):
    if not user_post.strip():
        st.warning("Please paste a post first!")
    else:
        # Score original
        original_score, original_reasons = score_post(user_post)
        
        st.markdown("---")
        st.markdown("### 📉 Your Original Post")
        st.error(f"**Score: {original_score}/100**")
        st.markdown("**What's wrong:**")
        for r in original_reasons:
            st.markdown(f"- {r}")

        # Optimize
        with st.spinner("✨ AI is rewriting your post..."):
            optimized = optimize_post(user_post)

        # Score optimized
        new_score, new_reasons = score_post(optimized)

        st.markdown("---")
        st.markdown("### ✨ Optimized Version")
        st.success(f"**New Score: {new_score}/100**")
        st.text_area("Copy your new post:", value=optimized, height=250)

        st.markdown("---")
        st.balloons()
        st.markdown(f"### 🎯 Score improved from **{original_score}** → **{new_score}** out of 100!")