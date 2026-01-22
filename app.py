import streamlit as st
import random
import copy

st.set_page_config(page_title="Moonie's Water Sort RPG", page_icon="🧪")

# ---------------------------------------------------------
# 1. 스타일 설정 (아이패드 호환성 패치 🍎)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 아이패드에서 버튼이 잘 보이도록 설정 */
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    
    /* 물병 안의 이모지 정렬 */
    .water-block {
        font-size: 2rem; /* 이모지 크기 */
        text-align: center;
        margin: 0;
        line-height: 1.5;
    }
    
    /* [핵심] 빈 공간과 숨겨진 화살표를 처리하는 클래스 */
    /* color: transparent 대신 opacity: 0을 써야 아이패드에서도 완벽하게 숨겨집니다 */
    .hidden-obj {
        opacity: 0; 
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 레벨 및 게임 로직
# ---------------------------------------------------------
def get_difficulty(level):
    if level <= 2: return 3
    elif level <= 5: return 4
    elif level <= 9: return 5
    elif level <= 14: return 6
    else: return 7 

COLORS = ['🟥', '🟦', '🟨', '🟩', '🟪', '🟧', '🟫', '⬛']

def init_game():
    current_level = st.session_state.level
    num_colors = get_difficulty(current_level)
    
    all_water = []
    chosen_colors = COLORS[:num_colors]
    for color in chosen_colors:
        all_water.extend([color] * 4)
    
    random.shuffle(all_water)
    
    bottles = []
    for i in range(num_colors):
        bottle = all_water[i*4 : (i+1)*4]
        bottles.append(bottle)
    
    bottles.append([])
    bottles.append([])
    
    st.session_state.bottles = bottles
    st.session_state.initial_bottles = copy.deepcopy(bottles)
    st.session_state.history = []
    st.session_state.selected_idx = None
    st.session_state.moves = 0
    st.session_state.game_over = False

if 'level' not in st.session_state:
    st.session_state.level = 1
    init_game()

# ---------------------------------------------------------
# 3. 사이드바
# ---------------------------------------------------------
with st.sidebar:
    st.title(f"🎖️ Lv.{st.session_state.level}")
    difficulty = get_difficulty(st.session_state.level)
    st.write(f"물병 개수: **{difficulty}개**")
    st.progress(min(1.0, st.session_state.level / 20))
    st.divider()
    
    if st.button("처음부터 다시 하기 (Reset) 💀"):
        st.session_state.level = 1
        init_game()
        st.rerun()

    st.divider()
    if st.button("되돌리기 (Undo) ↩️"):
        if st.session_state.history:
            st.session_state.bottles = st.session_state.history.pop()
            st.session_state.moves -= 1
            st.session_state.selected_idx = None
            st.rerun()
        else:
            st.toast("돌아갈 곳이 없어요!")

    if st.button("이 판 다시 도전 🔄"):
        st.session_state.bottles = copy.deepcopy(st.session_state.initial_bottles)
        st.session_state.history = []
        st.session_state.moves = 0
        st.session_state.game_over = False
        st.session_state.selected_idx = None
        st.rerun()

# ---------------------------------------------------------
# 4. 물 붓기 로직
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
            if color == water_color: same_color_count += 1
            else: break
        
        move_count = min(empty_space, same_color_count)
        for _ in range(move_count):
            dest.append(src.pop())
            
        st.session_state.moves += 1
        if check_victory(): st.session_state.game_over = True
    else:
        st.toast("색깔이 달라요! 🎨")

# ---------------------------------------------------------
# 5. 화면 그리기 (여기가 수정됨!)
# ---------------------------------------------------------
st.title(f"🧪 Water Sort (Lv.{st.session_state.level})")

c1, c2 = st.columns([1, 1])
c1.caption(f"Moves: {st.session_state.moves}")

if st.session_state.game_over:
    st.balloons()
    st.success(f"🎉 Level {st.session_state.level} Clear!")
    if st.button("🚀 다음 레벨 (Level Up!)", type="primary", use_container_width=True):
        st.session_state.level += 1
        init_game()
        st.rerun()

# 물병 배치
cols = st.columns(len(st.session_state.bottles))

for i, bottle in enumerate(st.session_state.bottles):
    with cols[i]:
        # [수정 1] 선택 화살표 처리
        # opacity: 0을 써서 공간은 차지하되, 눈에는 안 보이게 처리
        arrow_html = "🔻"
        arrow_class = "water-block"
        if st.session_state.selected_idx != i:
            arrow_class += " hidden-obj" # 선택 안 됐으면 투명도 0
            
        st.markdown(f"<div class='{arrow_class}'>{arrow_html}</div>", unsafe_allow_html=True)

        with st.container(border=True):
            display_bottle = bottle + ['EMPTY'] * (4 - len(bottle))
            
            for content in reversed(display_bottle):
                if content == 'EMPTY':
                    # [수정 2] 빈 공간 처리
                    # 투명한 빨간색 대신, 투명도 0인 빨간색을 사용해 높이를 맞춤
                    st.markdown("<div class='water-block hidden-obj'>🟥</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='water-block'>{content}</div>", unsafe_allow_html=True)
        
        # 버튼 처리
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
