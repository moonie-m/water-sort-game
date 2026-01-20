import streamlit as st
import random
import copy

st.set_page_config(page_title="Moonie's Water Sort RPG", page_icon="🧪")

# ---------------------------------------------------------
# 1. 레벨별 난이도 계산기 (AI 게임 마스터)
# ---------------------------------------------------------
def get_difficulty(level):
    # 레벨에 따라 물병 개수(색깔 수)를 자동으로 정해줍니다.
    if level <= 2:
        return 3 # Lv 1~2: 3개 (튜토리얼)
    elif level <= 5:
        return 4 # Lv 3~5: 4개 (쉬움)
    elif level <= 9:
        return 5 # Lv 6~9: 5개 (보통)
    elif level <= 14:
        return 6 # Lv 10~14: 6개 (어려움)
    else:
        # Lv 15부터는 7개 고정 (너무 많으면 화면 터짐)
        return 7 

# ---------------------------------------------------------
# 2. 게임 초기화
# ---------------------------------------------------------
COLORS = ['🟥', '🟦', '🟨', '🟩', '🟪', '🟧', '🟫', '⬛']

def init_game():
    # 현재 레벨에 맞는 난이도 가져오기
    current_level = st.session_state.level
    num_colors = get_difficulty(current_level)
    
    # (1) 색깔 생성
    all_water = []
    chosen_colors = COLORS[:num_colors]
    for color in chosen_colors:
        all_water.extend([color] * 4)
    
    # (2) 섞기
    random.shuffle(all_water)
    
    # (3) 병 담기
    bottles = []
    for i in range(num_colors):
        bottle = all_water[i*4 : (i+1)*4]
        bottles.append(bottle)
    
    # (4) 빈 병 2개 추가
    bottles.append([])
    bottles.append([])
    
    # (5) 상태 저장
    st.session_state.bottles = bottles
    st.session_state.initial_bottles = copy.deepcopy(bottles)
    st.session_state.history = []
    
    st.session_state.selected_idx = None
    st.session_state.moves = 0
    st.session_state.game_over = False

# [최초 실행 시] 레벨 1부터 시작
if 'level' not in st.session_state:
    st.session_state.level = 1
    init_game()

# ---------------------------------------------------------
# 3. 사이드바 (레벨 정보 & 도구)
# ---------------------------------------------------------
with st.sidebar:
    st.title(f"🎖️ Lv.{st.session_state.level}")
    
    # 난이도 정보 보여주기
    difficulty = get_difficulty(st.session_state.level)
    st.write(f"현재 난이도: **물병 {difficulty}개**")
    
    # 진행 상황 바 (시각적 재미)
    progress = min(1.0, st.session_state.level / 20)
    st.progress(progress, text="마스터를 향해!")

    st.divider()
    
    if st.button("처음부터 다시 하기 (Reset Level) 💀"):
        st.session_state.level = 1
        init_game()
        st.rerun()

    st.info("💡 팁: 레벨이 오를수록 물병 개수가 늘어납니다!")

    # 무리기 버튼
    st.divider()
    if st.button("한 수 무리기 (Undo) ↩️"):
        if st.session_state.history:
            last_state = st.session_state.history.pop()
            st.session_state.bottles = last_state
            st.session_state.moves -= 1
            st.session_state.selected_idx = None
            st.rerun()
        else:
            st.toast("돌아갈 과거가 없어요!")

    # 이 판 리셋 버튼
    if st.button("이 판 다시 도전 🔄"):
        st.session_state.bottles = copy.deepcopy(st.session_state.initial_bottles)
        st.session_state.history = []
        st.session_state.moves = 0
        st.session_state.game_over = False
        st.session_state.selected_idx = None
        st.rerun()

# ---------------------------------------------------------
# 4. 게임 로직
# ---------------------------------------------------------
def check_victory():
    for bottle in st.session_state.bottles:
        if len(bottle) == 0: continue
        if len(bottle) < 4: return False
        if len(set(bottle)) != 1: return False
    return True

def pour_water(src_idx, dest_idx):
    bottles = st.session_state.bottles
    src = bottles[src_idx]
    dest = bottles[dest_idx]

    if not src: return
    if len(dest) >= 4:
        st.toast("꽉 찼어요! 🚫")
        return

    water_color = src[-1]

    if not dest or dest[-1] == water_color:
        st.session_state.history.append(copy.deepcopy(bottles))

        empty_space = 4 - len(dest)
        same_color_count = 0
        for color in reversed(src):
            if color == water_color:
                same_color_count += 1
            else:
                break
        
        move_count = min(empty_space, same_color_count)
        
        for _ in range(move_count):
            dest.append(src.pop())
            
        st.session_state.moves += 1
        
        if check_victory():
            st.session_state.game_over = True
            
    else:
        st.toast("색깔이 달라요! 🎨")

# ---------------------------------------------------------
# 5. 화면 그리기
# ---------------------------------------------------------
st.title(f"🧪 Water Sort Puzzle (Lv.{st.session_state.level})")

c1, c2 = st.columns([1, 1])
c1.caption(f"이동 횟수: {st.session_state.moves}")
c2.caption(f"히스토리: {len(st.session_state.history)}")

# [승리 시 이벤트]
if st.session_state.game_over:
    st.balloons()
    st.success(f"🎉 축하합니다! Level {st.session_state.level} 클리어!")
    
    # [핵심] 다음 레벨 버튼이 화면 중앙에 큼지막하게 뜸
    if st.button("🚀 다음 레벨 도전하기 (Level Up!)", type="primary", use_container_width=True):
        st.session_state.level += 1 # 레벨 업!
        init_game() # 다음 단계 문제 출제
        st.rerun()

# 물병 배치
cols = st.columns(len(st.session_state.bottles))

for i, bottle in enumerate(st.session_state.bottles):
    with cols[i]:
        if st.session_state.selected_idx == i:
            st.markdown("<h3 style='text-align: center; color: red; margin: 0;'>🔻</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='text-align: center; color: transparent; margin: 0;'>🔻</h3>", unsafe_allow_html=True)

        with st.container(border=True):
            display_bottle = bottle + ['EMPTY'] * (4 - len(bottle))
            
            for content in reversed(display_bottle):
                if content == 'EMPTY':
                    st.markdown("## <span style='color:transparent'>🟥</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"## {content}")
        
        if not st.session_state.game_over:
            btn_label = "선택"
            btn_type = "secondary"
            if st.session_state.selected_idx == i:
                btn_label = "취소"
                btn_type = "primary"
            
            if st.button(btn_label, key=f"btn_{i}", type=btn_type, use_container_width=True):
                if st.session_state.selected_idx is None:
                    st.session_state.selected_idx = i
                    st.rerun()
                elif st.session_state.selected_idx == i:
                    st.session_state.selected_idx = None
                    st.rerun()
                else:
                    pour_water(st.session_state.selected_idx, i)
                    st.session_state.selected_idx = None
                    st.rerun()