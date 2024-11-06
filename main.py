import os
from glob import glob
import json
import pandas as pd
import streamlit as st
from submit import AIChallenge

st.set_page_config(page_title = "AIC Video Searching 🔍")

@st.cache_data
def load_videos(file_path):
    with open(file_path, "r") as data_file:
        return [x.strip() for x in data_file]
    
@st.cache_data
def load_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

@st.cache_resource
def load_csv(file_path):
    return pd.read_csv(file_path)

vids = load_videos("/Users/letri/Downloads/AIC/data.txt")

choices = st.multiselect("Video Search 🔍:", vids)
n = st.slider("Number of keyframes per video: ", 1, 30, 5)

submit_video = "video"
submit_time = "time"
if submit_video not in st.session_state:
    st.session_state[submit_video] = ""
if submit_time not in st.session_state:
    st.session_state[submit_time] = ""

# USIT.submit(USIT.kis("L03_V006", "876000"))
# USIT.submit(USIT.qa("6", "L01_V010", "177360"))

for choice in choices:
    vid, frame_id = choice.rsplit('_', 1)
    code = f'<{vid}><{frame_id}>'
    st.header(code)

    df = load_csv(f'/Users/letri/Downloads/AIC/map-keyframes/{vid}.csv')
    info = load_json(f'/Users/letri/Downloads/AIC/media-info/{vid}.json')

    time = []
    if vid not in st.session_state:
        st.session_state[vid] = 0

    df['time'] = df['pts_time'].apply(lambda x: f'{int(x) // 60}m{int(x) % 60}s')


    frame_id = int(frame_id)
    
    # calculate range(l, r)
    l_cost, r_cost = frame_id - n // 2, frame_id + n // 2 - (n % 2 == 0)
    l, r = max(1, l_cost), min(len(df.index) + 1, r_cost)
    if l == 1:
        r += abs(1 - l_cost)
    if r == len(df.index) + 1:
        l -= abs(r_cost - (len(df.index) + 1))
    
    st.table(df.iloc[l - 1 : r])
    id = vid.split('_')[0]
    rows = n // 5 + 1 # 5 cols per row
    remain = n
    for row in range(rows):
        num_of_cols = 5 if remain > 5 else remain
        cols = st.columns(5)
        for i in range(num_of_cols):
            with cols[i]:
                st.image(f'/Users/letri/Downloads/AIC/Dataset/Keyframes_{id}/{vid}/{(l):03}.jpg')
                html = f"""
                    <div style='text-align: center; background-color: #ff4b4b; font-size: 110%; border-radius: 3px'>{l}</div>
                """
                st.markdown(html, unsafe_allow_html = True)
                current_time = df['pts_time'][l - 1]
                button = st.button("→", key = l, use_container_width = True)
                if button:
                    st.session_state[submit_video] = vid
                    st.session_state[submit_time] = int(current_time * 1000)
                    st.session_state[vid] = current_time
                l += 1
        remain -= min(remain, 5)
    st.video(info["watch_url"], start_time = st.session_state[vid])
    st.divider()

USIT = AIChallenge()
login_session = "/Users/letri/Downloads/AIC/login_session.json"

try:
    USIT.load_session(login_session)
    assert len(USIT.get_evaluation_ids()) != 0
except:
    USIT.login("", "")
    USIT.save_session(login_session)

st.sidebar.title("AIC Submit")
USIT.assign_evaluation_id(st.sidebar.selectbox("Evaluation IDs:", USIT.get_evaluation_ids()))
is_qa_query = st.sidebar.toggle("qa-query")

answer = ""
if is_qa_query:
    answer = st.sidebar.text_input("answer")
video = st.sidebar.text_input("video", st.session_state[submit_video])
time = st.sidebar.text_input("time", st.session_state[submit_time])

query_type = "qa" if is_qa_query else "kis"
st.sidebar.write(f'{query_type}: {answer}-{video}-{time}')

if st.sidebar.button("Submit"):
    if is_qa_query:
        USIT.submit(USIT.qa(answer, video, time))
    else:
        USIT.submit(USIT.kis(video, time))
st.sidebar.write(USIT.status())
