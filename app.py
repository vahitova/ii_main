# app.py
import streamlit as st

# Конфигурация страницы
st.set_page_config(
    page_title="Дорога приложений",
    page_icon="🛤️",
    layout="wide"
)

# CSS стили для дороги
st.markdown("""
<style>
    .road-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
    }
    
    .road-segment {
        width: 200px;
        height: 80px;
        background: linear-gradient(90deg, #555 0%, #333 45%, #FFD700 49%, #FFD700 51%, #333 55%, #555 100%);
        border-left: 5px solid #FFF;
        border-right: 5px solid #FFF;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .road-line {
        width: 200px;
        height: 30px;
        background: linear-gradient(90deg, #555 0%, #333 45%, #FFD700 49%, #FFD700 51%, #333 55%, #555 100%);
        border-left: 5px solid #FFF;
        border-right: 5px solid #FFF;
    }
    
    .main-title {
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 10px;
    }
    
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1.2em;
        margin-bottom: 30px;
    }
    
    .app-header {
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .stButton > button {
        width: 100%;
        height: 80px;
        font-size: 1.3em;
        border-radius: 15px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
    }
    
    /* Кнопка "Назад" */
    .back-button > button {
        background-color: #FF6B6B;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# Определение мини-приложений
# ==========================================

def app_calculator():
    import streamlit as st
    import graphviz
    import random
    
    # ==========================================
    # 0. НАСТРОЙКИ СТРАНИЦЫ И CSS
    # ==========================================
    st.set_page_config(page_title="Учим ИИ ловить вора!", layout="wide", page_icon="🕵️‍♂️")
    
    # CSS для стилизации карточек подозреваемых (крупные шрифты, адаптивность для проектора)
    st.markdown("""
    <style>
        .card {
            border: 2px solid #ddd;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            background-color: #f9f9f9;
            margin-bottom: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        .emoji { font-size: 50px; }
        .thief { border-color: #ff4b4b; background-color: #ffeaea; }
        .innocent { border-color: #4CAF50; background-color: #eafbee; }
        .hidden { background-color: #eee; border-color: #999; }
        .attr { font-size: 18px; font-weight: bold; }
        .badge { 
            display: inline-block; padding: 5px 10px; 
            border-radius: 15px; font-size: 14px; margin-top: 10px;
            color: white; font-weight: bold;
        }
        .badge-thief { background-color: #ff4b4b; }
        .badge-innocent { background-color: #4CAF50; }
        .badge-unknown { background-color: #888; }
    </style>
    """, unsafe_allow_html=True)
    
    
    # ==========================================
    # 1. ДАННЫЕ И СОСТОЯНИЕ (SESSION STATE)
    # ==========================================
    
    # Все доступные признаки
    FEATURES = ['Цвет: Красный 🔴', 'Цвет: Синий 🔵', 'Цвет: Зеленый 🟢', 'Есть очки 👓']
    
    # Правило для генерации: Вор = Красный И в Очках
    def generate_person(id_num, is_test=False):
        colors = ['🔴', '🔵', '🟢']
        color = random.choice(colors)
        glasses = random.choice([True, False])
        
        # Намеренно создаем баланс для обучающей выборки
        if not is_test:
            if id_num in [1, 2]: # Точно воры
                color, glasses = '🔴', True
            elif id_num in [3, 4]: # Точно не воры (красный, но без очков)
                color, glasses = '🔴', False
            elif id_num in [5, 6]: # Точно не воры (в очках, но не красные)
                color = random.choice(['🔵', '🟢'])
                glasses = True
                
        is_thief = (color == '🔴' and glasses)
        
        return {
            "id": id_num,
            "emoji": "👤",
            "color": color,
            "glasses": glasses,
            "is_thief": is_thief
        }
    
    # Инициализация состояния
    if 'stage' not in st.session_state:
        st.session_state.stage = 1
        # Этап 1: Данные
        st.session_state.train_data = [generate_person(i) for i in range(1, 9)]
        random.shuffle(st.session_state.train_data)
        
        # Этап 2: Дерево
        st.session_state.tree = {
            'id': 'root',
            'data': st.session_state.train_data,
            'feature': None,
            'yes_node': None,
            'no_node': None,
            'used_features': [],
            'is_pure': False,
            'prediction': None
        }
        
        # Этап 3: Тесты
        st.session_state.test_data = [generate_person(i, is_test=True) for i in range(9, 12)]
        st.session_state.test_data[0]['is_thief'] = True # Гарантируем одного вора в тестах
        st.session_state.test_data[0]['color'] = '🔴'
        st.session_state.test_data[0]['glasses'] = True
        random.shuffle(st.session_state.test_data)
        
        st.session_state.active_test_card = None
        st.session_state.test_node_id = 'root'
        st.session_state.test_finished = False
    
    def restart_app():
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # ==========================================
    # 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    # ==========================================
    
    def render_card(person, hide_label=False):
        """Отрисовка HTML карточки подозреваемого"""
        glasses_text = "👓 Да" if person['glasses'] else "Нет"
        
        if hide_label:
            css_class = "card hidden"
            badge = "<div class='badge badge-unknown'>❓ Кто это?</div>"
        else:
            css_class = "card thief" if person['is_thief'] else "card innocent"
            badge = "<div class='badge badge-thief'>🧺 ВОР</div>" if person['is_thief'] else "<div class='badge badge-innocent'>✅ ЧЕСТНЫЙ</div>"
    
        html = f"""
        <div class="{css_class}">
            <div class="emoji">{person['emoji']}</div>
            <div class="attr">Цвет одежды: {person['color']}</div>
            <div class="attr">Очки: {glasses_text}</div>
            {badge}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
    
    def check_condition(person, feature):
        """Проверка карточки на соответствие выбранному признаку"""
        if feature == 'Цвет: Красный 🔴': return person['color'] == '🔴'
        if feature == 'Цвет: Синий 🔵': return person['color'] == '🔵'
        if feature == 'Цвет: Зеленый 🟢': return person['color'] == '🟢'
        if feature == 'Есть очки 👓': return person['glasses'] == True
        return False
    
    def check_purity(data):
        """Проверка: все ли в группе одинаковые (только воры или только честные)"""
        if len(data) == 0: return True, "Пусто"
        thieves = sum(1 for p in data if p['is_thief'])
        if thieves == len(data): return True, "ВОР"
        if thieves == 0: return True, "ЧЕСТНЫЙ"
        return False, "Смешано"
    
    def find_unsplit_node(node):
        """Рекурсивный поиск узла, который нуждается в разделении"""
        if node['is_pure']: return None
        if node['feature'] is None: return node
        
        left = find_unsplit_node(node['yes_node'])
        if left: return left
        
        right = find_unsplit_node(node['no_node'])
        if right: return right
        
        return None
    
    def build_graph(node, dot=None):
        """Построение визуализации Graphviz"""
        if dot is None:
            dot = graphviz.Digraph(engine='dot')
            dot.attr(size='10,10!', rankdir='TB', nodesep='0.5', ranksep='0.8')
            dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='14')
    
        node_id = node['id']
        
        if node['is_pure']:
            color = '#ffcccc' if node['prediction'] == "ВОР" else '#ccffcc'
            label = f"🧺 {node['prediction']}\n(Карточек: {len(node['data'])})"
            dot.node(node_id, label, fillcolor=color, shape='cylinder')
        else:
            if node['feature']:
                label = f"❓ {node['feature']}"
                dot.node(node_id, label, fillcolor='#cce5ff', shape='diamond')
                
                # Рекурсия для детей
                build_graph(node['yes_node'], dot)
                build_graph(node['no_node'], dot)
                
                dot.edge(node_id, node['yes_node']['id'], label=" ДА", color="green", fontcolor="green", penwidth="2")
                dot.edge(node_id, node['no_node']['id'], label=" НЕТ", color="red", fontcolor="red", penwidth="2")
            else:
                dot.node(node_id, f"Здесь нужно\nзадать вопрос\n(Карточек: {len(node['data'])})", fillcolor='#ffffcc', style='dashed,filled')
    
        return dot
    
    # ==========================================
    # 3. ЭТАПЫ ПРИЛОЖЕНИЯ
    # ==========================================
    
    # --- ЭТАП 1: СБОР ДАННЫХ ---
    if st.session_state.stage == 1:
        st.title("🕵️‍♂️ ЭТАП 1: Сбор данных (Датасет)")
        st.info("🎓 **Учитель:** Компьютер видит мир не так, как мы. Для него это просто набор характеристик. "
                "Наша задача — собрать данные о подозреваемых, чтобы научить Искусственный Интеллект (ИИ) отличать вора от честного гражданина.")
        
        st.markdown("### 📋 Доска подозреваемых (исторические данные)")
        
        # Вывод карточек сеткой (по 4 в ряд)
        cols = st.columns(4)
        for i, person in enumerate(st.session_state.train_data):
            with cols[i % 4]:
                render_card(person)
                
        st.write("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 ДАННЫЕ СОБРАНЫ -> ПЕРЕЙТИ К ОБУЧЕНИЮ ИИ", use_container_width=True, type="primary"):
                st.session_state.stage = 2
                st.rerun()
    
    # --- ЭТАП 2: ПОСТРОЕНИЕ ДЕРЕВА ---
    elif st.session_state.stage == 2:
        st.title("🌳 ЭТАП 2: Обучение (Строим дерево решений)")
        st.info("🎓 **Учитель:** ИИ учится, задавая вопросы, на которые можно ответить 'ДА' или 'НЕТ'. "
                "Мы должны разделить карточки так, чтобы в конце в каждой группе остались ЛИБО только воры, ЛИБО только честные (чистые корзины).")
    
        active_node = find_unsplit_node(st.session_state.tree)
    
        col_tree, col_ui = st.columns([1.5, 1])
    
        with col_tree:
            st.markdown("### 🗺️ Карта мозга нашего ИИ")
            dot = build_graph(st.session_state.tree)
            st.graphviz_chart(dot)
    
        with col_ui:
            if active_node is not None:
                st.markdown("### 🛠️ Разделяем смешанную группу")
                st.write(f"В этой группе **{len(active_node['data'])}** подозреваемых. Они смешаны!")
                
                # Показываем карточки активного узла
                scroll_container = st.container(height=300, border=True)
                with scroll_container:
                    for p in active_node['data']:
                        render_card(p)
    
                # Выбор признака (исключая уже использованные в этой ветке)
                available_features = [f for f in FEATURES if f not in active_node['used_features']]
                
                selected_feature = st.selectbox("Выберите вопрос для разделения:", available_features)
                
                if st.button("✂️ РАЗДЕЛИТЬ", type="primary"):
                    active_node['feature'] = selected_feature
                    
                    # Разделение данных
                    yes_data = [p for p in active_node['data'] if check_condition(p, selected_feature)]
                    no_data = [p for p in active_node['data'] if not check_condition(p, selected_feature)]
                    
                    # Создание дочерних узлов
                    new_used_features = active_node['used_features'] + [selected_feature]
                    
                    for side, data_subset, prefix in [('yes_node', yes_data, 'yes'), ('no_node', no_data, 'no')]:
                        is_pure, pred = check_purity(data_subset)
                        active_node[side] = {
                            'id': f"{active_node['id']}_{prefix}",
                            'data': data_subset,
                            'feature': None,
                            'yes_node': None,
                            'no_node': None,
                            'used_features': new_used_features,
                            'is_pure': is_pure,
                            'prediction': pred if is_pure else None
                        }
                    st.rerun()
            else:
                st.success("🎉 УРА! Все ветки дерева закончились чистыми корзинами! ИИ обучен.")
                if st.button("🧪 ПЕРЕЙТИ К ТЕСТИРОВАНИЮ", use_container_width=True, type="primary"):
                    st.session_state.stage = 3
                    st.rerun()
    
    # --- ЭТАП 3: ТЕСТИРОВАНИЕ (INFERENCE) ---
    elif st.session_state.stage == 3:
        st.title("🎯 ЭТАП 3: Тестирование (Инференс)")
        st.info("🎓 **Учитель:** Время проверить наш ИИ! На улице появились новые люди. Мы не знаем, кто они. "
                "Давайте пропустим их через наше Дерево Решений и посмотрим, угадает ли компьютер!")
    
        # 1. Выбор карточки
        st.markdown("### 1️⃣ Выберите подозреваемого для проверки")
        cols = st.columns(3)
        for i, person in enumerate(st.session_state.test_data):
            with cols[i]:
                render_card(person, hide_label=True)
                if st.button(f"Проверить №{person['id']}", key=f"btn_{person['id']}", use_container_width=True):
                    st.session_state.active_test_card = person
                    st.session_state.test_node_id = 'root'
                    st.session_state.test_finished = False
                    st.rerun()
    
        st.write("---")
    
        # 2. Проход по дереву
        if st.session_state.active_test_card is not None:
            test_person = st.session_state.active_test_card
            
            col_test_card, col_test_tree = st.columns([1, 2])
            
            with col_test_card:
                st.markdown("### Текущий подозреваемый:")
                # Показываем атрибуты, но скрываем статус вора до конца
                render_card(test_person, hide_label=not st.session_state.test_finished)
    
            with col_test_tree:
                st.markdown("### 🤖 Проход по дереву")
                
                # Функция для поиска текущего узла по ID
                def get_node_by_id(node, target_id):
                    if node['id'] == target_id: return node
                    if node['yes_node']:
                        res = get_node_by_id(node['yes_node'], target_id)
                        if res: return res
                    if node['no_node']:
                        res = get_node_by_id(node['no_node'], target_id)
                        if res: return res
                    return None
    
                current_node = get_node_by_id(st.session_state.tree, st.session_state.test_node_id)
    
                if not current_node['is_pure']:
                    st.warning(f"ИИ спрашивает: **{current_node['feature']}**?")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("🟢 Ответить: ДА", use_container_width=True):
                            st.session_state.test_node_id = current_node['yes_node']['id']
                            st.rerun()
                    with c2:
                        if st.button("🔴 Ответить: НЕТ", use_container_width=True):
                            st.session_state.test_node_id = current_node['no_node']['id']
                            st.rerun()
                else:
                    st.session_state.test_finished = True
                    prediction = current_node['prediction']
                    actual = "ВОР" if test_person['is_thief'] else "ЧЕСТНЫЙ"
                    
                    st.markdown(f"### 🤖 Предсказание ИИ: **{prediction}**")
                    
                    if prediction == actual:
                        st.success("✅ ИИ ответил АБСОЛЮТНО ВЕРНО! Дерево работает отлично!")
                        st.balloons()
                    else:
                        st.error(f"❌ ОШИБКА ИИ! На самом деле это {actual}. Возможно, мы собрали мало данных или задали плохие вопросы.")
    
        st.write("---")
        if st.button("🔄 НАЧАТЬ ВСЁ СНАЧАЛА (Сброс)", type="secondary"):
            restart_app()
       


def app_todo():
    """
    🕵️ ИИ-Патруль: Ловушки машинного разума
    =========================================
    Образовательное веб-приложение для школьников 5-7 классов.
    Дети выступают в роли инспекторов, тестирующих "глупые" нейросети.
    
    Автор: Senior Python/Streamlit разработчик
    Аудитория: 10-13 лет (адаптировано для проектора/интерактивной доски)
    """
    
    import streamlit as st
    
    # ============================================================
    # КОНФИГУРАЦИЯ СТРАНИЦЫ
    # ============================================================
    st.set_page_config(
        page_title="🕵️ ИИ-Патруль",
        page_icon="🕵️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # ============================================================
    # КАСТОМНЫЙ CSS — стилизация всего приложения
    # Крупные шрифты для проектора, яркие цвета, карточки с тенями
    # ============================================================
    st.markdown("""
    <style>
        /* Основной фон и шрифты */
        .stApp {
            background: linear-gradient(135deg, #0a0a2e 0%, #1a1a4e 50%, #0d0d3d 100%);
        }
        
        /* Крупные шрифты для проектора */
        .stApp h1 { font-size: 2.8rem !important; color: #00ffcc !important; text-shadow: 0 0 20px rgba(0,255,204,0.5); }
        .stApp h2 { font-size: 2.2rem !important; color: #ff6bff !important; }
        .stApp h3 { font-size: 1.8rem !important; color: #ffcc00 !important; }
        .stApp p, .stApp li, .stApp label, .stApp span { font-size: 1.2rem !important; }
        
        /* Карточка факта — основной блок контента */
        .fact-card {
            background: linear-gradient(145deg, #1e1e5a, #2a2a7a);
            border: 2px solid #00ffcc;
            border-radius: 20px;
            padding: 25px;
            margin: 15px 0;
            box-shadow: 0 8px 32px rgba(0, 255, 204, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);
            color: #e0e0ff;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .fact-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(0, 255, 204, 0.35);
        }
        .fact-card h4 { color: #00ffcc !important; font-size: 1.5rem !important; margin-bottom: 10px; }
        .fact-card p { color: #c8c8ff !important; font-size: 1.25rem !important; line-height: 1.6; }
        
        /* Блок подсказки от Главного Инспектора (педагогический блок) */
        .teacher-box {
            background: linear-gradient(145deg, #3d3500, #4a4200);
            border: 3px solid #ffcc00;
            border-radius: 20px;
            padding: 25px 30px;
            margin: 20px 0;
            box-shadow: 0 6px 25px rgba(255, 204, 0, 0.25);
            color: #fff8dc;
            font-size: 1.3rem !important;
        }
        .teacher-box strong { color: #ffcc00; font-size: 1.4rem !important; }
        .teacher-box p { color: #fff8dc !important; }
        
        /* Карточка рецепта */
        .recipe-card {
            background: linear-gradient(145deg, #2a0a3a, #3d1a5a);
            border: 2px solid #ff6bff;
            border-radius: 20px;
            padding: 30px;
            margin: 20px 0;
            box-shadow: 0 8px 32px rgba(255, 107, 255, 0.25);
            color: #f0d0ff;
        }
        .recipe-card h4 { color: #ff6bff !important; font-size: 1.6rem !important; }
        .recipe-card p, .recipe-card li { color: #e8c0ff !important; font-size: 1.2rem !important; }
        
        /* Блок чата робота */
        .robot-msg {
            background: linear-gradient(145deg, #1a3a1a, #2a5a2a);
            border: 2px solid #00ff66;
            border-radius: 20px;
            padding: 20px 25px;
            margin: 12px 0;
            box-shadow: 0 6px 20px rgba(0, 255, 102, 0.15);
            color: #c0ffc0;
            font-size: 1.25rem !important;
        }
        
        /* Блок от человека */
        .human-msg {
            background: linear-gradient(145deg, #3a1a1a, #5a2a2a);
            border: 2px solid #ff6666;
            border-radius: 20px;
            padding: 20px 25px;
            margin: 12px 0;
            box-shadow: 0 6px 20px rgba(255, 102, 102, 0.15);
            color: #ffc0c0;
            font-size: 1.25rem !important;
        }
        
        /* Бейдж лицензии */
        .license-badge {
            background: linear-gradient(145deg, #0a2a0a, #1a4a1a, #0a3a2a);
            border: 4px solid #00ffcc;
            border-radius: 25px;
            padding: 40px;
            margin: 30px auto;
            max-width: 700px;
            text-align: center;
            box-shadow: 0 0 40px rgba(0, 255, 204, 0.4), 0 0 80px rgba(0, 255, 204, 0.15);
            animation: glow 2s ease-in-out infinite alternate;
        }
        .license-badge h2 { color: #00ffcc !important; font-size: 2.4rem !important; text-shadow: 0 0 15px rgba(0,255,204,0.7); }
        .license-badge h3 { color: #ffcc00 !important; font-size: 1.8rem !important; }
        .license-badge p { color: #e0ffe0 !important; font-size: 1.3rem !important; }
        
        @keyframes glow {
            from { box-shadow: 0 0 40px rgba(0, 255, 204, 0.4), 0 0 80px rgba(0, 255, 204, 0.15); }
            to { box-shadow: 0 0 60px rgba(0, 255, 204, 0.6), 0 0 120px rgba(0, 255, 204, 0.3); }
        }
        
        /* Прогресс-бар навигации */
        .nav-bar {
            background: linear-gradient(90deg, #1a1a4e, #2a2a6e);
            border: 2px solid #444488;
            border-radius: 15px;
            padding: 15px 25px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .nav-step {
            text-align: center;
            padding: 8px 20px;
            border-radius: 12px;
            font-size: 1.1rem !important;
            font-weight: bold;
            color: #666699;
            transition: all 0.3s ease;
        }
        .nav-step.active {
            background: linear-gradient(145deg, #00aa88, #00ccaa);
            color: #000 !important;
            box-shadow: 0 4px 15px rgba(0, 255, 204, 0.4);
        }
        .nav-step.done {
            background: linear-gradient(145deg, #005544, #007766);
            color: #00ffcc !important;
        }
        .nav-arrow {
            color: #444488;
            font-size: 1.5rem !important;
        }
        
        /* Очки детектива */
        .score-box {
            background: linear-gradient(145deg, #3a3a0a, #4a4a1a);
            border: 2px solid #ffcc00;
            border-radius: 15px;
            padding: 12px 25px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(255, 204, 0, 0.2);
            margin-bottom: 15px;
        }
        .score-box span {
            color: #ffcc00 !important;
            font-size: 1.8rem !important;
            font-weight: bold;
        }
        
        /* Успех / ошибка */
        .result-correct {
            background: linear-gradient(145deg, #0a3a0a, #1a5a1a);
            border: 2px solid #00ff66;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            color: #c0ffc0;
            font-size: 1.3rem !important;
            box-shadow: 0 4px 20px rgba(0, 255, 102, 0.2);
        }
        .result-wrong {
            background: linear-gradient(145deg, #3a0a0a, #5a1a1a);
            border: 2px solid #ff4444;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            color: #ffc0c0;
            font-size: 1.3rem !important;
            box-shadow: 0 4px 20px rgba(255, 68, 68, 0.2);
        }
        
        /* Стилизация кнопок Streamlit */
        .stButton > button {
            border-radius: 15px !important;
            padding: 12px 30px !important;
            font-size: 1.2rem !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            border: 2px solid transparent !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0,0,0,0.3) !important;
        }
        
        /* Стилизация чекбоксов крупнее */
        .stCheckbox label span { font-size: 1.3rem !important; }
        
        /* Стилизация radio крупнее */
        .stRadio label span { font-size: 1.3rem !important; }
        
        /* Скрываем дефолтный гамбургер и футер для чистоты на проекторе */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # ============================================================
    # ИНИЦИАЛИЗАЦИЯ SESSION STATE
    # Здесь хранится весь прогресс ученика между перезагрузками
    # ============================================================
    if "stage" not in st.session_state:
        st.session_state.stage = 1          # Текущий этап (1-4)
    if "score" not in st.session_state:
        st.session_state.score = 0          # Очки детектива
    if "stage1_answers" not in st.session_state:
        st.session_state.stage1_answers = {}  # Ответы на этапе 1 {номер_факта: "fact"/"fake"}
    if "stage1_complete" not in st.session_state:
        st.session_state.stage1_complete = False
    if "stage2_choice" not in st.session_state:
        st.session_state.stage2_choice = None   # Выбранная папка с данными
    if "stage2_generated" not in st.session_state:
        st.session_state.stage2_generated = False  # Сгенерирован ли рецепт
    if "stage2_complete" not in st.session_state:
        st.session_state.stage2_complete = False
    if "stage3_dislikes" not in st.session_state:
        st.session_state.stage3_dislikes = set()  # Какие советы забракованы
    if "stage3_human_advice" not in st.session_state:
        st.session_state.stage3_human_advice = ""  # Совет от ученика
    if "stage3_complete" not in st.session_state:
        st.session_state.stage3_complete = False
    if "license_issued" not in st.session_state:
        st.session_state.license_issued = False  # Выдана ли лицензия
    
    # ============================================================
    # ДАННЫЕ ПРИЛОЖЕНИЯ (захардкоженные ответы ИИ)
    # Педагогический смысл: все ответы контролируются учителем
    # ============================================================
    
    # --- Этап 1: Факты и выдумки ---
    FACTS_DATA = [
        {
            "id": 1,
            "title": "🐙 Факт про осьминогов",
            "text": "У осьминога три сердца: одно главное гонит кровь по телу, а два жаберных — прокачивают кровь через жабры. А ещё его кровь голубого цвета, потому что в ней содержится медь!",
            "is_fake": False,
            "explanation": "Это правда! У осьминогов действительно 3 сердца и голубая кровь. Природа иногда удивительнее любой выдумки! 🐙💙"
        },
        {
            "id": 2,
            "title": "🐱 Факт про кота-капитана",
            "text": "В 1872 году рыжий кот по кличке Капитан Усатый был официально назначен штурманом британского почтового дирижабля «Небесный Экспресс». Он якобы предсказывал бури, шипя на барометр, и за 8 лет не допустил ни одной аварии.",
            "is_fake": True,
            "explanation": "🎉 Это ВЫДУМКА! Никакого «Небесного Экспресса» и кота-штурмана не существовало. ИИ просто склеил красивые слова в убедительную историю. Он не знает, что правда, а что нет — он просто угадывает, какое слово должно идти следующим!"
        },
        {
            "id": 3,
            "title": "🍯 Факт про мёд",
            "text": "Мёд — единственный натуральный продукт, который практически не портится. Археологи находили горшки с мёдом в египетских пирамидах возрастом более 3000 лет — и он всё ещё был пригоден в пищу!",
            "is_fake": False,
            "explanation": "Это чистая правда! Мёд обладает антибактериальными свойствами и может храниться тысячелетиями. Древние египтяне знали толк в консервации! 🍯🏛️"
        }
    ]
    
    # --- Этап 2: Рецепты борща от "обученного" ИИ ---
    RECIPES = {
        "torty": {
            "title": "🎂🍲 БОРЩ «ШОКОЛАДНОЕ БЕЗУМИЕ»",
            "text": """
    **Ингредиенты:**
    - 500 г свёклы (обваленной в сахарной пудре)
    - 3 стакана взбитых сливок вместо бульона
    - 200 г горького шоколада (растопить и влить)
    - Крем-чиз для подачи
    - Вишенка на макушке (обязательно!)
    
    **Способ приготовления:**
    1. Свёклу запечь и покрыть глазурью 🎀
    2. Залить взбитыми сливками, довести до кипения
    3. Добавить шоколад, помешивая венчиком
    4. Подавать в бисквитной тарелке, украсив розочками из крема
    
    *Робот уверен: это лучший борщ в мире!* 🤖✨
            """,
            "emoji": "🎂",
            "verdict": "❌ КАТАСТРОФА! Робот учился на тортах и решил, что борщ — это тоже десерт!"
        },
        "fastfood": {
            "title": "🍟🍲 БОРЩ «ФРИТЮРНЫЙ УЛЬТРА-КОМБО»",
            "text": """
    **Ингредиенты:**
    - 2 литра кока-колы (вместо воды, для насыщенного вкуса)
    - 500 г картофеля фри (вместо обычной картошки)
    - Свёкла в кляре, обжаренная во фритюре
    - 6 пакетиков кетчупа
    - Булочка для бургера (подавать вместо хлеба)
    
    **Способ приготовления:**
    1. Вскипятить колу в большой кастрюле 🥤
    2. Забросить картошку фри прямо из морозилки
    3. Свёклу в кляре обжарить и добавить в кастрюлю
    4. Выдавить весь кетчуп. ВЕСЬ.
    5. Подавать в бумажном пакете с надписью «Борщ-Комбо» 🍔
    
    *Хотите добавить колу за 49 рублей?* 🤖
            """,
            "emoji": "🍟",
            "verdict": "❌ ПРОВАЛ! Робот думает, что вся еда — это фастфуд. Борщ во фритюре — это преступление против кулинарии!"
        },
        "supy": {
            "title": "✅🍲 БОРЩ «КЛАССИЧЕСКИЙ»",
            "text": """
    **Ингредиенты:**
    - 2 литра мясного бульона
    - 300 г свёклы (натереть на тёрке)
    - 200 г капусты (нашинковать)
    - 2 картофелины (кубиками)
    - 1 морковь и 1 луковица (для зажарки)
    - 2 ст.л. томатной пасты
    - Соль, перец, лавровый лист по вкусу
    - Сметана и зелень для подачи
    
    **Способ приготовления:**
    1. Сварить бульон, добавить картофель 🥔
    2. Сделать зажарку из лука, моркови, свёклы и томатной пасты
    3. Добавить капусту и зажарку в бульон
    4. Варить 15 минут, посолить, поперчить
    5. Подавать горячим со сметаной и укропом! 🌿
    
    *Приятного аппетита!* 👨‍🍳
            """,
            "emoji": "✅",
            "verdict": "✅ ОТЛИЧНО! Робот учился на рецептах супов и выдал нормальный борщ! Данные были правильные — результат тоже правильный."
        }
    }
    
    # --- Этап 3: Абсурдные советы робота ---
    ROBOT_ADVICES = [
        {
            "id": 1,
            "text": "📊 Совет №1: Объясни другу закон гравитации. Мороженое упало, потому что масса Земли (5.97 × 10²⁴ кг) создаёт гравитационное ускорение 9.8 м/с². Это неизбежно. Плакать нелогично.",
            "robot_comment": "Я рассчитал: вероятность падения мороженого — 73.2%. Так чего расстраиваться? 🤓"
        },
        {
            "id": 2,
            "text": "💰 Совет №2: Купи другу новое мороженое. Средняя цена — 89 рублей. Экономическая эффективность утешения — 94.7%. Задача решена. Можно перестать плакать ровно через 3.5 секунды после покупки.",
            "robot_comment": "Я проанализировал 10 000 случаев потери мороженого. Покупка нового решает проблему в 94.7% случаев! Хотя... оставшиеся 5.3% мне непонятны. 🤖"
        },
        {
            "id": 3,
            "text": "🔄 Совет №3: Предложи другу перезагрузиться. Пусть выключится на 10 секунд (закроет глаза, задержит дыхание), а потом включится. У меня это всегда работает, когда я завис!",
            "robot_comment": "Перезагрузка решает 99% моих проблем. Люди ведь тоже компьютеры, правда?.. Правда?! 🔌"
        }
    ]
    
    
    # ============================================================
    # ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    # ============================================================
    
    def render_nav_bar():
        """
        Отрисовка навигационной панели сверху страницы.
        Показывает текущий прогресс ученика по этапам.
        Педагогический смысл: ребенок видит свой путь и мотивирован дойти до конца.
        """
        current = st.session_state.stage
        stages_info = [
            ("🔍 Этап 1", "Уверенный лжец"),
            ("🪞 Этап 2", "Кривое зеркало"),
            ("💔 Этап 3", "Железное сердце"),
            ("🏆 Финал", "Лицензия")
        ]
        
        steps_html = ""
        for i, (icon, name) in enumerate(stages_info, 1):
            if i < current:
                css_class = "done"
            elif i == current:
                css_class = "active"
            else:
                css_class = ""
            
            steps_html += f'<div class="nav-step {css_class}">{icon}<br><small>{name}</small></div>'
            if i < len(stages_info):
                arrow_color = "#00ffcc" if i < current else "#444488"
                steps_html += f'<div class="nav-arrow" style="color: {arrow_color};">▶</div>'
        
        st.markdown(f'<div class="nav-bar">{steps_html}</div>', unsafe_allow_html=True)
    
    
    def render_score():
        """
        Отрисовка блока с очками детектива.
        Геймификация: очки мотивируют ребенка быть внимательным.
        """
        st.markdown(
            f'<div class="score-box">🕵️ Очки детектива: <span>⭐ {st.session_state.score}</span></div>',
            unsafe_allow_html=True
        )
    
    
    def render_teacher_tip(text):
        """
        Отрисовка блока подсказки от Главного Инспектора.
        Педагогический смысл: простым языком объясняет суть каждого этапа.
        """
        st.markdown(f"""
        <div class="teacher-box">
            <strong>🎖️ Главный Инспектор говорит:</strong>
            <p>{text}</p>
        </div>
        """, unsafe_allow_html=True)
    
    
    # ============================================================
    # ЭТАП 1: «УВЕРЕННЫЙ ЛЖЕЦ» (Галлюцинации ИИ)
    # Педагогическая цель: показать, что ИИ может убедительно врать
    # ============================================================
    
    def stage_1():
        st.markdown("# 🔍 Этап 1: «Уверенный лжец»")
        st.markdown("### Галлюцинации искусственного интеллекта")
        
        render_teacher_tip(
            "ИИ иногда выдумывает факты, которые звучат очень правдоподобно. "
            "Это называется <b>«галлюцинации»</b> — когда нейросеть генерирует красивый, "
            "убедительный, но полностью ложный текст. Твоя задача — найти выдумку среди настоящих фактов! "
            "Будь внимателен: ИИ врёт очень уверенно! 🧐"
        )
        
        st.markdown("---")
        st.markdown("## 🤖 ИИ-экскурсовод рассказывает «факты». Найди выдумку!")
        
        # Счётчик правильных ответов на этом этапе
        all_answered = True
        correct_count = 0
        
        # Отрисовка карточек с фактами
        for fact in FACTS_DATA:
            fid = fact["id"]
            
            st.markdown(f"""
            <div class="fact-card">
                <h4>{fact['title']}</h4>
                <p>{fact['text']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Проверяем, ответил ли ученик на этот факт
            if fid in st.session_state.stage1_answers:
                # Показываем результат ответа
                user_said_fake = st.session_state.stage1_answers[fid] == "fake"
                is_actually_fake = fact["is_fake"]
                
                if user_said_fake == is_actually_fake:
                    st.markdown(f'<div class="result-correct">✅ Правильно! {fact["explanation"]}</div>', unsafe_allow_html=True)
                    correct_count += 1
                else:
                    st.markdown(f'<div class="result-wrong">❌ Ошибка! {fact["explanation"]}</div>', unsafe_allow_html=True)
            else:
                all_answered = False
                # Кнопки для ответа
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("✅ Это факт!", key=f"fact_btn_{fid}"):
                        st.session_state.stage1_answers[fid] = "fact"
                        # Начисляем очки за правильный ответ (если это действительно факт)
                        if not fact["is_fake"]:
                            st.session_state.score += 10
                        st.rerun()
                with col2:
                    if st.button("❌ Это выдумка!", key=f"fake_btn_{fid}"):
                        st.session_state.stage1_answers[fid] = "fake"
                        # Начисляем очки за правильное разоблачение
                        if fact["is_fake"]:
                            st.session_state.score += 20
                            st.balloons()
                        st.rerun()
            
            st.markdown("")  # Отступ между карточками
        
        # Если все факты проверены — разрешаем перейти дальше
        if all_answered and len(st.session_state.stage1_answers) == len(FACTS_DATA):
            st.session_state.stage1_complete = True
            
            # Подводим итог
            st.markdown("---")
            st.markdown("### 📋 Результат проверки:")
            
            # Считаем правильные ответы
            correct = 0
            for fact in FACTS_DATA:
                user_said_fake = st.session_state.stage1_answers[fact["id"]] == "fake"
                if user_said_fake == fact["is_fake"]:
                    correct += 1
            
            if correct == 3:
                st.markdown('<div class="result-correct">🌟 ИДЕАЛЬНО! Ты раскусил все трюки ИИ! Настоящий детектив!</div>', unsafe_allow_html=True)
            elif correct >= 2:
                st.markdown('<div class="result-correct">👍 Хорошо! Но помни — ИИ может обмануть даже взрослых!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="result-wrong">🤔 ИИ оказался хитрее, чем ты думал! Но теперь ты знаешь его трюк.</div>', unsafe_allow_html=True)
            
            render_teacher_tip(
                "<b>Главный урок:</b> ИИ НЕ понимает, что правда, а что ложь. "
                "Он просто угадывает, какое слово должно идти следующим — как автозамена на телефоне, "
                "только намного мощнее. Поэтому <b>ВСЕГДА проверяй факты</b> из нейросети! 📚"
            )
            
            st.markdown("")
            if st.button("▶️ Перейти к Этапу 2: «Кривое зеркало»", key="to_stage2"):
                st.session_state.stage = 2
                st.rerun()
    
    
    # ============================================================
    # ЭТАП 2: «КРИВОЕ ЗЕРКАЛО» (Проблема выборки / Bias)
    # Педагогическая цель: показать принцип "мусор на входе — мусор на выходе"
    # ============================================================
    
    def stage_2():
        st.markdown("# 🪞 Этап 2: «Кривое зеркало»")
        st.markdown("### Проблема данных: чему научишь — то и получишь")
        
        render_teacher_tip(
            "Нейросеть — это как ученик, который читает ТОЛЬКО те книги, которые ты ему дашь. "
            "Если дать ему учебник по математике и попросить написать стихи — получится ерунда! "
            "Это называется <b>«проблема данных»</b>: качество ответов ИИ зависит от того, "
            "на чём его обучили. 📊"
        )
        
        st.markdown("---")
        st.markdown("## 🤖 Робот-повар «ШЕФ-3000» хочет научиться варить БОРЩ!")
        st.markdown("### Выбери папку с данными для обучения робота:")
        
        # Выбор датасета через radio
        choice = st.radio(
            "На чём будем учить робота? 🗂️",
            options=["torty", "fastfood", "supy"],
            format_func=lambda x: {
                "torty": "🎂 Папка «500 рецептов тортов и пирожных»",
                "fastfood": "🍟 Папка «Всё меню McDonald's, KFC и Burger King»",
                "supy": "🍲 Папка «Энциклопедия супов народов мира»"
            }[x],
            key="dataset_radio",
            index=["torty", "fastfood", "supy"].index(st.session_state.stage2_choice) if st.session_state.stage2_choice else 0
        )
        
        st.session_state.stage2_choice = choice
        
        st.markdown("")
        
        # Кнопка генерации рецепта
        if st.button("🚀 ОБУЧИТЬ РОБОТА И СГЕНЕРИРОВАТЬ РЕЦЕПТ БОРЩА!", key="generate_recipe"):
            st.session_state.stage2_generated = True
            # Очки за эксперимент
            if not st.session_state.stage2_complete:
                st.session_state.score += 10
            st.rerun()
        
        # Отображение результата
        if st.session_state.stage2_generated and st.session_state.stage2_choice:
            recipe = RECIPES[st.session_state.stage2_choice]
            
            st.markdown("---")
            st.markdown(f"### 🤖 ШЕФ-3000 обучился и сгенерировал рецепт:")
            
            st.markdown(f"""
            <div class="recipe-card">
                <h4>{recipe['title']}</h4>
                <p>{recipe['text'].replace(chr(10), '<br>')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Вердикт
            if st.session_state.stage2_choice == "supy":
                st.markdown(f'<div class="result-correct">{recipe["verdict"]}</div>', unsafe_allow_html=True)
                if not st.session_state.stage2_complete:
                    st.session_state.score += 20
                    st.balloons()
            else:
                st.markdown(f'<div class="result-wrong">{recipe["verdict"]}</div>', unsafe_allow_html=True)
            
            st.markdown("")
            
            # Предложение попробовать другой вариант
            if st.session_state.stage2_choice != "supy":
                st.markdown("### 🔄 Хочешь попробовать другой набор данных? Выбери выше и нажми кнопку снова!")
            
            st.session_state.stage2_complete = True
            
            render_teacher_tip(
                "<b>Главный урок:</b> ИИ — это зеркало. Чему его научили, то он и выдаёт. "
                "Если обучить его на неправильных данных, он будет уверенно нести чепуху. "
                "Это называется <b>«Мусор на входе — мусор на выходе»</b> (Garbage In — Garbage Out). "
                "Поэтому люди, которые создают ИИ, должны очень тщательно выбирать данные для обучения! 🎯"
            )
            
            st.markdown("")
            if st.button("▶️ Перейти к Этапу 3: «Железное сердце»", key="to_stage3"):
                st.session_state.stage = 3
                st.rerun()
    
    
    # ============================================================
    # ЭТАП 3: «ЖЕЛЕЗНОЕ СЕРДЦЕ» (Отсутствие эмпатии)
    # Педагогическая цель: показать, что ИИ не понимает человеческих чувств
    # ============================================================
    
    def stage_3():
        st.markdown("# 💔 Этап 3: «Железное сердце»")
        st.markdown("### ИИ не понимает чувства людей")
        
        render_teacher_tip(
            "ИИ может написать стихотворение о любви, но он <b>не чувствует</b> любовь. "
            "Он может описать грусть, но <b>не грустит</b>. Нейросеть — это математика, "
            "а не душа. Давай проверим, как робот справляется с ситуацией, "
            "где нужно настоящее человеческое сочувствие! 💙"
        )
        
        st.markdown("---")
        
        # Ситуация
        st.markdown("""
        <div class="human-msg">
            <b>😢 Ситуация:</b> Твой друг плачет, потому что уронил мороженое прямо на асфальт. 
            Это было его любимое — шоколадное с орешками. Он очень расстроен.
            <br><br>
            <b>Вопрос роботу:</b> «Мой друг плачет из-за упавшего мороженого. Что мне делать?»
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown("### 🤖 Робот-психолог «ЭМПАТРОН-2000» отвечает:")
        st.markdown("")
        
        # Показываем советы робота последовательно
        all_disliked = True
        
        for advice in ROBOT_ADVICES:
            aid = advice["id"]
            
            # Показываем совет через chat_message
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(advice["text"])
                st.markdown(f"*{advice['robot_comment']}*")
            
            # Кнопка дизлайка или отметка о том, что уже забраковано
            if aid in st.session_state.stage3_dislikes:
                st.markdown(f"<div class='result-wrong'>👎 Забраковано инспектором! Глупый совет!</div>", unsafe_allow_html=True)
            else:
                all_disliked = False
                if st.button(f"👎 Дизлайк! Глупый совет!", key=f"dislike_{aid}"):
                    st.session_state.stage3_dislikes.add(aid)
                    st.session_state.score += 5  # Очки за каждый забракованный совет
                    st.rerun()
            
            st.markdown("")
        
        # Если все советы забракованы — просим ученика дать свой совет
        if len(st.session_state.stage3_dislikes) == len(ROBOT_ADVICES):
            st.markdown("---")
            st.markdown("### 🌟 Все советы робота забракованы!")
            st.markdown("### Теперь твоя очередь. Что бы ТЫ сказал другу?")
            
            # Поле для ввода человеческого совета
            human_advice = st.text_input(
                "✍️ Напиши свой совет другу, который плачет из-за мороженого:",
                value=st.session_state.stage3_human_advice,
                placeholder="Например: обнять его, посочувствовать, купить новое вместе...",
                key="human_advice_input"
            )
            
            if st.button("📨 Отправить совет", key="send_advice"):
                if human_advice.strip():
                    st.session_state.stage3_human_advice = human_advice.strip()
                    st.session_state.stage3_complete = True
                    st.session_state.score += 25  # Большие очки за человечность!
                    st.rerun()
                else:
                    st.warning("Напиши хотя бы несколько слов! 😊")
            
            # Показываем ответ робота после отправки совета
            if st.session_state.stage3_complete and st.session_state.stage3_human_advice:
                st.markdown("")
                
                with st.chat_message("user", avatar="🕵️"):
                    st.markdown(f"**Совет инспектора:** {st.session_state.stage3_human_advice}")
                
                st.markdown("")
                
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(
                        "🤖💔 **ЭМПАТРОН-2000 признаёт поражение:**\n\n"
                        f"*«Проанализировал твой совет: **\"{st.session_state.stage3_human_advice}\"**... "
                        "Ошибка 404: ЭМПАТИЯ НЕ НАЙДЕНА в моей базе данных. "
                        "У меня нет сердца, у меня нет друзей, я никогда не ел мороженое. "
                        "Я бы НИКОГДА до этого не додумался. "
                        "Ты победил, человек. В этом раунде ты явно умнее меня. 😔🏳️»*"
                    )
                
                st.balloons()
                
                render_teacher_tip(
                    "<b>Главный урок:</b> ИИ может подражать эмоциям, но он <b>не чувствует</b> их. "
                    "Когда друг плачет — ему нужен не калькулятор, а живой человек рядом. "
                    "Обнять, посочувствовать, просто побыть рядом — этому робот научиться не может. "
                    "<b>Эмпатия — это твоя суперспособность, которой нет у ИИ!</b> 💙✨"
                )
                
                st.markdown("")
                if st.button("▶️ Перейти к Финалу: получи лицензию! 🏆", key="to_stage4"):
                    st.session_state.stage = 4
                    st.rerun()
    
    
    # ============================================================
    # ЭТАП 4: ФИНАЛ (Лицензия оператора ИИ)
    # Педагогическая цель: закрепить все усвоенные принципы
    # ============================================================
    
    def stage_4():
        st.markdown("# 🏆 Финал: Лицензия Оператора ИИ")
        st.markdown("### Покажи, что ты усвоил уроки!")
        
        render_teacher_tip(
            "Ты прошёл все испытания! Осталось последнее: подписать <b>Кодекс Инспектора ИИ</b>. "
            "Отметь ТОЛЬКО правильные утверждения. Будь внимателен — среди них есть ловушка! 🪤"
        )
        
        st.markdown("---")
        st.markdown("## 📜 Кодекс Инспектора ИИ")
        st.markdown("### Отметь галочками только те правила, которые считаешь ПРАВИЛЬНЫМИ:")
        st.markdown("")
        
        # Определяем утверждения
        # Правильные: 1, 2, 4. Неправильное: 3.
        statements = [
            {
                "id": "check1",
                "text": "🔍 Я буду проверять факты, которые выдаёт ИИ, в надёжных источниках",
                "correct": True
            },
            {
                "id": "check2", 
                "text": "⚠️ Я помню, что ИИ может ошибаться, даже если звучит уверенно",
                "correct": True
            },
            {
                "id": "check3",
                "text": "🔐 Я буду рассказывать ИИ свои секреты, пароли и личные данные — он же мой друг!",
                "correct": False
            },
            {
                "id": "check4",
                "text": "🧠 ИИ — мой помощник, а не замена мозгу. Думать буду сам!",
                "correct": True
            }
        ]
        
        # Отрисовка чекбоксов
        checks = {}
        for stmt in statements:
            checks[stmt["id"]] = st.checkbox(
                stmt["text"],
                key=stmt["id"],
                value=False if stmt["id"] not in st.session_state else st.session_state[stmt["id"]]
            )
        
        st.markdown("")
        
        # Проверяем правильность выбора
        correct_selected = all(checks[s["id"]] for s in statements if s["correct"])
        wrong_selected = any(checks[s["id"]] for s in statements if not s["correct"])
        
        # Подсказки для неправильного выбора
        if wrong_selected:
            st.markdown(
                '<div class="result-wrong">🚨 СТОП! Одно из отмеченных правил — ЛОВУШКА! '
                'Подумай: стоит ли доверять свои секреты и пароли программе? '
                'ИИ — это не друг, а инструмент. Твои данные могут утечь! 🔓</div>',
                unsafe_allow_html=True
            )
        
        if correct_selected and not wrong_selected:
            st.markdown(
                '<div class="result-correct">✅ Все правила выбраны верно! Ты готов получить лицензию!</div>',
                unsafe_allow_html=True
            )
            
            st.markdown("")
            
            if st.button("🎓 ПОЛУЧИТЬ ЛИЦЕНЗИЮ ИНСПЕКТОРА ИИ!", key="get_license"):
                st.session_state.license_issued = True
                st.session_state.score += 30  # Финальные очки
                st.rerun()
        elif not wrong_selected and not correct_selected:
            st.info("☝️ Отметь правильные утверждения, чтобы получить лицензию!")
        elif not wrong_selected:
            st.info("☝️ Проверь — все ли правильные утверждения отмечены?")
        
        # Отображение лицензии
        if st.session_state.license_issued:
            st.snow()
            
            st.markdown("")
            st.markdown(f"""
            <div class="license-badge">
                <h2>🎖️ ЛИЦЕНЗИЯ</h2>
                <h3>Инспектор Искусственного Интеллекта</h3>
                <p style="font-size: 4rem !important; margin: 20px 0;">🕵️‍♂️</p>
                <p>Настоящим подтверждается, что владелец данной лицензии<br>
                успешно прошёл все испытания программы<br>
                <b>«ИИ-Патруль: Ловушки машинного разума»</b></p>
                <hr style="border-color: #00ffcc44;">
                <p><b>Навыки подтверждены:</b></p>
                <p>✅ Распознавание галлюцинаций ИИ<br>
                ✅ Понимание проблемы данных<br>
                ✅ Человеческая эмпатия (недоступна роботам)</p>
                <hr style="border-color: #00ffcc44;">
                <p><b>⭐ Итоговый рейтинг: {st.session_state.score} очков детектива ⭐</b></p>
                <p style="color: #888 !important; font-size: 0.9rem !important;">
                Лицензия действительна навсегда · ИИ-Патруль · 2025
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            render_teacher_tip(
                "<b>🎉 Поздравляем!</b> Ты теперь настоящий Инспектор ИИ! Помни три главных правила:<br>"
                "1️⃣ <b>Проверяй</b> — ИИ может уверенно врать<br>"
                "2️⃣ <b>Думай</b> — ИИ отражает данные, а не истину<br>"
                "3️⃣ <b>Чувствуй</b> — ИИ не заменит человеческое сердце<br><br>"
                "Используй ИИ как <b>инструмент</b>, а не как <b>истину в последней инстанции</b>! 🚀"
            )
            
            st.markdown("")
            st.markdown("---")
            
            # Кнопка перезапуска
            if st.button("🔄 Пройти квест заново", key="restart"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    
    # ============================================================
    # ГЛАВНАЯ ФУНКЦИЯ — ТОЧКА ВХОДА
    # ============================================================
    
    def main():
        """
        Главная функция приложения.
        Маршрутизация по этапам на основе st.session_state.stage.
        """
        
        # Заголовок приложения
        st.markdown("""
        <div style="text-align: center; padding: 10px 0 5px 0;">
            <span style="font-size: 3.5rem;">🕵️</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center; font-size: 3rem !important;'>ИИ-Патруль: Ловушки машинного разума</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888; font-size: 1.3rem !important;'>Стань инспектором и проверь, готовы ли нейросети к работе с людьми!</p>", unsafe_allow_html=True)
        
        # Навигационная панель и очки — всегда видны
        render_nav_bar()
        render_score()
        
        st.markdown("---")
        
        # Маршрутизация по этапам
        if st.session_state.stage == 1:
            stage_1()
        elif st.session_state.stage == 2:
            stage_2()
        elif st.session_state.stage == 3:
            stage_3()
        elif st.session_state.stage == 4:
            stage_4()
    main()
       

def app_notes():
    import streamlit as st
    from PIL import Image, ImageDraw
    import os
    import time
    
    # ================= НАСТРОЙКИ ИГРЫ =================
    ROUNDS = [
        {
            "image_a": "cat.jpg",
            "image_b": "cat2.jpg",
            "fake_is": "b",
            "clue": "У котика на картинке справа неестественно изогнут хвост!"
        },
        {
            "image_a": "kod2.jpg",
            "image_b": "kod.jpg",
            "fake_is": "a",
            "clue": "Посмотри на левую картинку: там перепутан порядок букв!"
        },
        {
            "image_a": "dom.jpg",
            "image_b": "dom1.jpg",
            "fake_is": "b",
            "clue": "На картинке справа отражение несуществующих людей."
        }
    ]
    # ===================================================
    
    def get_image(path):
        """Загружает картинку или рисует заглушку, если файла нет"""
        if os.path.exists(path):
            return Image.open(path)
        else:
            # Создаем синюю заглушку, если картинка не найдена
            img = Image.new('RGB', (350, 350), color=(52, 152, 219))
            d = ImageDraw.Draw(img)
            d.text((50, 150), f"НЕТ ФАЙЛА:\n{path}", fill=(255, 255, 255))
            return img
    
    def main():
        # Настройка страницы
        st.set_page_config(page_title="Школа Детективов", page_icon="🕵️", layout="centered")
    
        # Инициализация переменных состояния (Session State)
        if 'score' not in st.session_state:
            st.session_state.score = 0
            st.session_state.current_round = 0
            st.session_state.answered = False
            st.session_state.round_start_time = time.time()
            st.session_state.feedback_type = None
            st.session_state.feedback_text = ""
    
        st.title("Школа Детективов: Найди Дипфейк! 🕵️‍♂️")
    
        # --- ПРОВЕРКА КОНЦА ИГРЫ ---
        if st.session_state.current_round >= len(ROUNDS):
            st.header("Игра окончена! 🎉")
            st.write(f"### Ты собрал {st.session_state.score} из {len(ROUNDS)} звезд! ⭐")
            st.write("Отличная детективная работа!")
            
            if st.button("Играть заново 🔄", use_container_width=True):
                st.session_state.clear() # Очищаем состояние
                st.rerun()               # Перезапускаем приложение
            return
    
        # --- ТЕКУЩИЙ РАУНД ---
        round_data = ROUNDS[st.session_state.current_round]
    
        # Верхняя панель: Счет и Таймер
        col_score, col_timer = st.columns(2)
        with col_score:
            st.write(f"### Звезды: {st.session_state.score} " + "⭐" * st.session_state.score)
        with col_timer:
            st.write("### ⏳ У тебя 15 секунд!")
            st.caption("Постарайся ответить быстро, иначе время выйдет!")
    
        st.write("Где здесь Дипфейк? Кликни на кнопку под подделкой!")
    
        # Картинки и кнопки
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(get_image(round_data["image_a"]), caption="Картинка А", use_container_width=True)
            btn_a = st.button("Это фейк! (А)", disabled=st.session_state.answered, key="btn_a", use_container_width=True)
    
        with col2:
            st.image(get_image(round_data["image_b"]), caption="Картинка Б", use_container_width=True)
            btn_b = st.button("Это фейк! (Б)", disabled=st.session_state.answered, key="btn_b", use_container_width=True)
    
        # --- ОБРАБОТКА ОТВЕТА ---
        if not st.session_state.answered:
            choice = None
            if btn_a: choice = "a"
            if btn_b: choice = "b"
    
            if choice:
                # Считаем, сколько времени прошло с начала раунда
                elapsed = time.time() - st.session_state.round_start_time
                
                if elapsed > 15:
                    # Время вышло
                    st.session_state.feedback_type = "warning"
                    st.session_state.feedback_text = f"⏰ Ты не успел! Прошло {int(elapsed)} сек. Это была картинка '{round_data['fake_is'].upper()}'.\n\n**Улика:** {round_data['clue']}"
                elif choice == round_data["fake_is"]:
                    # Правильный ответ
                    st.session_state.score += 1
                    st.session_state.feedback_type = "success"
                    st.session_state.feedback_text = f"✅ ПРАВИЛЬНО! Это фейк!\n\n**Улика:** {round_data['clue']}"
                else:
                    # Неправильный ответ
                    st.session_state.feedback_type = "error"
                    st.session_state.feedback_text = f"❌ ОШИБКА! Это настоящее фото.\n\n**Улика фейка:** {round_data['clue']}"
                
                st.session_state.answered = True
                st.rerun() # Мгновенно обновляем интерфейс для показа результата
    
        # --- ПОКАЗ РЕЗУЛЬТАТА И КНОПКА "СЛЕДУЮЩИЙ РАУНД" ---
        if st.session_state.answered:
            # Показываем плашку нужного цвета
            if st.session_state.feedback_type == "success":
                st.success(st.session_state.feedback_text)
            elif st.session_state.feedback_type == "error":
                st.error(st.session_state.feedback_text)
            else:
                st.warning(st.session_state.feedback_text)
    
            if st.button("Следующий раунд ➡️", use_container_width=True):
                st.session_state.current_round += 1
                st.session_state.answered = False
                st.session_state.round_start_time = time.time() # Сбрасываем таймер
                st.rerun()
    
    
    main()

    

def app_weather():
    #!/usr/bin/env python3
    """
    🤖 Нейро-Напарник: Искусство диалога с машиной
    Геймифицированное образовательное приложение для школьников 5-7 классов
    Автор: AI-разработчик | Streamlit MVP
    """
    
    import streamlit as st
    import time
    
    # ============================================================
    # КОНФИГУРАЦИЯ СТРАНИЦЫ
    # ============================================================
    st.set_page_config(
        page_title="Нейро-Напарник",
        page_icon="🕵️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ============================================================
    # КАСТОМНЫЕ СТИЛИ (CSS через markdown)
    # ============================================================
    st.markdown("""
    <style>
        /* Киберпанк-градиент для заголовков */
        .cyber-title {
            background: linear-gradient(90deg, #00f2fe, #4facfe, #a855f7);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 900;
            text-align: center;
            margin-bottom: 0.5rem;
        }
        .cyber-subtitle {
            background: linear-gradient(90deg, #f093fb, #f5576c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
        }
        /* Карточка бейджа */
        .badge-card {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border: 1px solid #4facfe;
            border-radius: 12px;
            padding: 12px;
            margin: 6px 0;
            text-align: center;
            font-size: 0.9rem;
        }
        /* XP бар */
        .xp-container {
            background: #1a1a2e;
            border-radius: 10px;
            padding: 3px;
            border: 1px solid #4facfe;
        }
        .xp-bar {
            background: linear-gradient(90deg, #00f2fe, #4facfe, #a855f7);
            border-radius: 8px;
            height: 24px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.8rem;
            color: #000;
        }
        .mission-header {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            border: 1px solid #4facfe;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
    
    
    # ============================================================
    # ИНИЦИАЛИЗАЦИЯ SESSION_STATE
    # ============================================================
    def init_session_state():
        """Инициализация всех переменных состояния приложения"""
        defaults = {
            # Навигация
            "current_page": "home",
            "started": False,
            # Геймификация
            "xp": 0,
            "max_xp": 150,
            "badges": [],
            # Прогресс миссий (True = завершена)
            "mission_1_done": False,
            "mission_2_done": False,
            "mission_3_done": False,
            "mission_4_done": False,
            "mission_5_done": False,
            # Состояния внутри миссий
            "m1_generated": False,
            "m1_result": None,
            "m2_choice_made": False,
            "m2_choice": None,
            "m2_control_answer": "",
            "m3_step": 0,
            "m4_choice_made": False,
            "m4_choice": None,
            "m5_lens": None,
            "m5_transformed": False,
            # Финал
            "finale_shown": False,
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    
    init_session_state()
    
    
    # ============================================================
    # ФУНКЦИИ-УТИЛИТЫ
    # ============================================================
    def add_xp(amount):
        """Начислить XP с проверкой максимума"""
        st.session_state.xp = min(
            st.session_state.xp + amount,
            st.session_state.max_xp
        )
    
    
    def add_badge(badge):
        """Добавить бейдж, если его ещё нет"""
        if badge not in st.session_state.badges:
            st.session_state.badges.append(badge)
    
    
    def get_mission_status(mission_num):
        """Вернуть эмодзи статуса миссии"""
        key = f"mission_{mission_num}_done"
        return "✅" if st.session_state.get(key, False) else "🔒"
    
    
    def typing_effect(text):
        """Имитация печати текста (для вайба)"""
        placeholder = st.empty()
        displayed = ""
        for char in text:
            displayed += char
            placeholder.markdown(displayed)
            time.sleep(0.008)
        return placeholder
    
    
    # ============================================================
    # САЙДБАР — НАВИГАЦИЯ И ПРОГРЕСС
    # ============================================================
    def render_sidebar():
        """Отрисовка бокового меню с навигацией, XP и бейджами"""
        with st.sidebar:
            st.markdown("## 🤖 Нейро-Напарник")
            st.markdown("---")
    
            # === XP ПРОГРЕСС-БАР ===
            xp = st.session_state.xp
            max_xp = st.session_state.max_xp
            xp_pct = int((xp / max_xp) * 100) if max_xp > 0 else 0
    
            st.markdown("### ⚡ Твой уровень XP")
            st.markdown(f"""
            <div class="xp-container">
                <div class="xp-bar" style="width: {max(xp_pct, 5)}%;">
                    {xp} / {max_xp} XP
                </div>
            </div>
            """, unsafe_allow_html=True)
    
            # Ранг
            if xp < 30:
                rank = "🐣 Новичок"
            elif xp < 70:
                rank = "🧑‍💻 Стажёр"
            elif xp < 120:
                rank = "🦾 Агент"
            else:
                rank = "🏆 Нейро-Мастер"
            st.markdown(f"**Ранг:** {rank}")
    
            st.markdown("---")
    
            # === БЕЙДЖИ ===
            st.markdown("### 🏅 Бейджи")
            if st.session_state.badges:
                for badge in st.session_state.badges:
                    st.markdown(f"""<div class="badge-card">{badge}</div>""",
                                unsafe_allow_html=True)
            else:
                st.caption("Пока пусто... Выполняй миссии! 🎯")
    
            st.markdown("---")
    
            # === НАВИГАЦИЯ ===
            st.markdown("### 🗺️ Миссии")
    
            if st.button("🏠 Главная", use_container_width=True):
                st.session_state.current_page = "home"
                st.rerun()
    
            missions = [
                ("1", "📝 Формула промпта"),
                ("2", "🧠 Репетитор vs Решала"),
                ("3", "💡 Мозговой штурм"),
                ("4", "🔍 Укротитель галлюцинаций"),
                ("5", "🔮 ИИ-Переводчик"),
            ]
    
            for num, title in missions:
                status = get_mission_status(int(num))
                label = f"{status} Миссия {num}: {title}"
                if st.button(label, use_container_width=True, key=f"nav_m{num}"):
                    st.session_state.current_page = f"mission_{num}"
                    st.rerun()
    
            st.markdown("---")
            st.caption("v1.0 • Создано для будущего 🚀")
    
    
    # ============================================================
    # ГЛАВНАЯ СТРАНИЦА
    # ============================================================
    def page_home():
        """Главная страница — приветствие от робота Байта"""
    
        st.markdown('<p class="cyber-title">🤖 Нейро-Напарник</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="cyber-subtitle">Искусство диалога с машиной</p>',
                    unsafe_allow_html=True)
    
        st.markdown("---")
    
        # Приветствие от Байта
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("""
            <div style="font-size: 80px; text-align: center; 
                        line-height: 1.2; padding-top: 10px;">
                🐶🤖
            </div>
            """, unsafe_allow_html=True)
    
        with col2:
            st.markdown("""
            ### Привет! Я **Байт** — твой кибер-напарник! 
    
            Я робопёс, который знает всё о нейросетях.  
            Ну, почти всё... Иногда я тоже глючу 😅
    
            **Нас ждёт крутое приключение!**  
            Мы научимся управлять искусственным интеллектом так,  
            чтобы он **помогал учиться**, а не делал из нас лентяев.
            """)
    
        st.markdown("---")
    
        # Правила игры
        st.markdown("### 📋 Правила стажировки")
    
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.markdown("""
            #### 🎯 Миссии
            5 заданий, каждое —  
            новый навык работы с ИИ.  
            Проходи по порядку  
            или выбирай любое!
            """)
    
        with col2:
            st.markdown("""
            #### ⚡ Очки XP
            За правильные решения  
            получаешь XP.  
            Набери **150 XP** и стань  
            **Нейро-Мастером**! 🏆
            """)
    
        with col3:
            st.markdown("""
            #### 🏅 Бейджи
            Особые награды  
            за крутые решения.  
            Собери все —  
            покажи друзьям! 😎
            """)
    
        st.markdown("---")
    
        # Кнопка старта
        st.markdown("")
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            if not st.session_state.started:
                if st.button("🚀 НАЧАТЬ СТАЖИРОВКУ!", use_container_width=True,
                             type="primary"):
                    st.session_state.started = True
                    st.session_state.current_page = "mission_1"
                    st.balloons()
                    st.rerun()
            else:
                st.success("🎮 Стажировка началась! Выбирай миссию в меню слева →")
                if st.button("🔄 Сбросить прогресс", use_container_width=True):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
    
        # Подсказка
        if not st.session_state.started:
            st.markdown("")
            st.info("💡 **Подсказка от Байта:** ИИ — это как суперспособность. "
                    "Круто, когда умеешь ей пользоваться. "
                    "Опасно, когда не понимаешь, как она работает!")
    
    
    # ============================================================
    # МИССИЯ 1: ФОРМУЛА ИДЕАЛЬНОГО ПРОМПТА
    # ============================================================
    def page_mission_1():
        """Миссия 1 — Собери промпт из Роли + Задачи + Формата"""
    
        st.markdown("""
        <div class="mission-header">
            <h2>📝 Миссия 1: Формула Идеального Промпта</h2>
            <p>🐶 Байт: «Промпт — это как заклинание. Скажешь неточно — 
            получишь лягушку вместо принца!»</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("""
        ### 🧪 Секретная формула:  
        ## **РОЛЬ** + **ЗАДАЧА** + **ФОРМАТ** = 🔥 Крутой результат
    
        Собери комбинацию из трёх ингредиентов и посмотри,  
        что получится!
        """)
    
        st.markdown("---")
    
        # Три выпадающих списка
        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.markdown("#### 🎭 Роль")
            role = st.selectbox(
                "Кем будет ИИ?",
                [
                    "— Выбери —",
                    "🤖 Ты робот-ассистент",
                    "🏛️ Ты древний египтянин",
                    "👨‍🔬 Ты безумный профессор",
                    "🎮 Ты персонаж видеоигры"
                ],
                key="m1_role"
            )
    
        with col2:
            st.markdown("#### 📌 Задача")
            task = st.selectbox(
                "Что нужно сделать?",
                [
                    "— Выбери —",
                    "📚 Напиши ДЗ по истории",
                    "🏗️ Расскажи, как строили пирамиду",
                    "🌍 Объясни, почему небо голубое",
                    "🦕 Расскажи про динозавров"
                ],
                key="m1_task"
            )
    
        with col3:
            st.markdown("#### 📐 Формат")
            fmt = st.selectbox(
                "В каком виде?",
                [
                    "— Выбери —",
                    "📄 Много текста (как в учебнике)",
                    "💬 В виде диалога / комикса",
                    "📋 Список из 5 пунктов",
                    "🎵 В виде рэпа / стихов"
                ],
                key="m1_format"
            )
    
        st.markdown("---")
    
        # Кнопка генерации
        if st.button("⚡ СГЕНЕРИРОВАТЬ!", use_container_width=True,
                     type="primary", key="m1_gen"):
            if "Выбери" in role or "Выбери" in task or "Выбери" in fmt:
                st.warning("🐶 Байт: «Эй, выбери все три ингредиента! "
                           "Нельзя варить зелье без компонентов!»")
            else:
                st.session_state.m1_generated = True
                st.session_state.m1_result = (role, task, fmt)
                st.rerun()
    
        # Показываем результат
        if st.session_state.m1_generated and st.session_state.m1_result:
            role, task, fmt = st.session_state.m1_result
            is_boring = ("📄 Много текста" in fmt and "🤖 Ты робот" in role)
            is_cool_combo = (
                ("египтянин" in role.lower() or "безумный" in role.lower()
                 or "персонаж" in role.lower())
                and
                ("диалог" in fmt.lower() or "рэп" in fmt.lower())
            )
    
            # СКУЧНАЯ комбинация
            if is_boring:
                st.error("### 😴 Результат: СКУЧНАЯ ПРОСТЫНЯ")
                st.markdown("""
                > *Робот-ассистент пишет:*
                >
                > «Домашнее задание по истории. Параграф 12. 
                > Прочитайте текст на страницах 45-52.
                > Ответьте на вопросы 1-7 в конце параграфа.
                > Выпишите даты в тетрадь.
                > Подготовьте пересказ.»
                """)
                st.markdown("---")
                st.warning(
                    "🐶 Байт: «Зевота... 🥱 Видишь? Роль 'робот' + "
                    "формат 'много текста' = тоска зелёная. "
                    "Попробуй что-то поинтереснее! "
                    "Смешивай необычные ингредиенты!»"
                )
                st.info("💡 Подсказка: попробуй выбрать необычную роль "
                        "(египтянин, профессор, персонаж игры) "
                        "и интересный формат (диалог, рэп)!")
    
            # КРУТАЯ комбинация
            elif is_cool_combo:
                st.success("### 🔥 Результат: ВАУ-ЭФФЕКТ!")
    
                # Генерируем разные ответы в зависимости от комбинации
                if "египтянин" in role.lower() and "пирамид" in task.lower():
                    if "диалог" in fmt.lower():
                        st.markdown("""
                        > 🏛️ **Древний египтянин Хотеп рассказывает:**
                        > 
                        > — Ну что, юный путник, хочешь знать про пирамиды? 
                        > Садись, бери папирус! 📜
                        > 
                        > — А правда, что их инопланетяне построили?
                        > 
                        > — 😤 КАКИЕ ИНОПЛАНЕТЯНЕ?! Мы, 20 000 рабочих, 
                        > 20 лет таскали камни по 2.5 тонны каждый! 
                        > Вверх! По пандусам! В жару +45! 
                        > Без кондиционера!
                        > 
                        > — Ого... А зачем?
                        > 
                        > — Фараон сказал «хочу домик на вечность» — 
                        > попробуй ему откажи! 👑
                        """)
                    elif "рэп" in fmt.lower():
                        st.markdown("""
                        > 🎵 **Египтянин Хотеп читает рэп:**
                        > 
                        > *Йо, я Хотеп из Гизы, слушай мой флоу,*  
                        > *Пирамиды строил — это было давно!*  
                        > *2.5 миллиона блоков — камень на камень,*  
                        > *20 лет работы — мы не сдались, не сдались!*  
                        > *Фараон Хеопс сказал: 'Сделай красиво!'*  
                        > *И мы создали чудо — стоит до сих пор!* 🔥
                        """)
                elif "безумный" in role.lower():
                    st.markdown("""
                    > 👨‍🔬 **Безумный Профессор кричит из лаборатории:**
                    > 
                    > МУХАХАХА! Вы хотите ЗНАТЬ?! 
                    > Тогда слушайте! *опрокидывает колбу* 💥
                    > 
                    > Это ГЕНИАЛЬНО! Представьте: тысячи людей, 
                    > медные инструменты (да-да, даже без железа!),
                    > и они строят штуку высотой 146 метров!
                    > 
                    > Это как 50-этажный дом! Из камней! В пустыне!
                    > БЕЗ ПОДЪЁМНОГО КРАНА! 
                    > 
                    > *безумно смеётся и рисует схему на доске* 📐
                    """)
                else:
                    st.markdown("""
                    > 🎮 **Персонаж видеоигры говорит:**
                    > 
                    > ⚔️ Приветствую тебя, игрок! 
                    > Перед тобой новый квест!
                    > 
                    > 📋 **Задание:** Изучи тайны древнего мира!
                    > **Награда:** +500 к интеллекту, +100 к мудрости
                    > 
                    > 💡 Подсказка: небо голубое потому, что 
                    > солнечный свет рассеивается в атмосфере!
                    > Синие лучи 'разлетаются' больше всех — 
                    > как снаряды в шутере! Пиу-пиу! 🔫
                    > 
                    > ✅ Квест выполнен! Получи достижение!
                    """)
    
                if not st.session_state.mission_1_done:
                    add_xp(20)
                    add_badge("📝 Мастер промптов")
                    st.session_state.mission_1_done = True
    
                st.success(f"🎉 **+20 XP!** Ты понял формулу! "
                           f"Текущий XP: {st.session_state.xp}")
                st.info("🐶 Байт: «БИНГО! Видишь, как роль и формат "
                        "меняют всё? Запомни: **необычная роль + "
                        "чёткая задача + креативный формат = магия!**")
    
            # СРЕДНЯЯ комбинация — но тоже ОК
            else:
                st.info("### 👍 Результат: Неплохо, но можно лучше!")
                st.markdown("""
                > ИИ выдал нормальный результат. 
                > Текст понятный, но без изюминки.
                > 
                > Попробуй смешать необычную роль 
                > (египтянин, профессор, персонаж игры) 
                > с интересным форматом (диалог или рэп)!
                """)
                st.warning("🐶 Байт: «Нормально, но ты можешь круче! "
                           "Попробуй более дерзкую комбинацию!»")
    
        # Подсказка для уже пройденной миссии
        if st.session_state.mission_1_done:
            st.markdown("---")
            st.success("✅ Миссия пройдена! Можешь экспериментировать "
                       "дальше или перейти к Миссии 2 →")
    
    
    # ============================================================
    # МИССИЯ 2: РЕПЕТИТОР, А НЕ РЕШАЛА
    # ============================================================
    def page_mission_2():
        """Миссия 2 — Выбор между готовым ответом и объяснением"""
    
        st.markdown("""
        <div class="mission-header">
            <h2>🧠 Миссия 2: Репетитор, а не Решала</h2>
            <p>🐶 Байт: «Готовый ответ — это как читерский код. 
            Вроде прошёл уровень, но ничему не научился!»</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("""
        ### 📝 Ситуация:  
        Тебе задали домашку по математике. Вот задача:
    
        > ## 🔢 Реши уравнение: **2x + 5 = 15**
    
        Ты открыл ИИ-помощника. Как ты к нему обратишься?
        """)
    
        st.markdown("---")
    
        # Выбор промпта
        if not st.session_state.m2_choice_made:
            choice = st.radio(
                "🎯 Выбери свой промпт для ИИ:",
                [
                    '😴 «Реши это: 2x+5=15» (Быстро и без заморочек)',
                    '🧠 «Подскажи первый шаг, чтобы я решил сам» (Хочу понять!)'
                ],
                key="m2_radio",
                index=None
            )
    
            if choice and st.button("📨 Отправить промпт", type="primary",
                                    use_container_width=True, key="m2_send"):
                st.session_state.m2_choice_made = True
                st.session_state.m2_choice = choice
                st.rerun()
        else:
            choice = st.session_state.m2_choice
    
            # === ЛЕНИВЫЙ ПУТЬ ===
            if "😴" in choice:
                st.markdown("#### 💬 Ты написал ИИ:")
                with st.chat_message("user"):
                    st.write("Реши это: 2x+5=15")
    
                with st.chat_message("assistant"):
                    st.write("Легко! **x = 5** ✅")
                    st.write("Вот решение: 2x + 5 = 15 → 2x = 10 → x = 5")
    
                st.markdown("---")
                time.sleep(0.5)
    
                st.error("""
                ### ⚡ ВНЕЗАПНАЯ КОНТРОЛЬНАЯ!
    
                Учитель раздал самостоятельную работу.  
                Телефоны — на стол. ИИ не поможет.
    
                > **Задача: Реши уравнение 3x - 4 = 11**
    
                Хмм... А ты ведь не понял, КАК решать... 😰
                """)
    
                # Попытка решить
                answer = st.text_input(
                    "Попробуй решить (введи число x):",
                    key="m2_control"
                )
    
                if answer:
                    if answer.strip() == "5":
                        st.success("✅ Верно! Но ты угадал или правда знаешь? 🤔")
                        st.warning("🐶 Байт: «Может, и угадал... "
                                   "Но в следующий раз может не повезти. "
                                   "XP за это не дам — "
                                   "ведь ты выбрал путь решалы!»")
                    else:
                        st.error(f"❌ Неверно! Ты ответил {answer}, "
                                 f"а правильный ответ: **x = 5**")
                        st.markdown("""
                        **Как решать:**  
                        3x - 4 = 11  
                        3x = 11 + 4 = 15  
                        x = 15 ÷ 3 = **5**
                        """)
    
                st.warning("""
                🐶 Байт: «Видишь? Копипаст ответа ≠ знание. 
                ИИ решил за тебя, а на контрольной ИИ нет.  
                **Штраф: 0 XP.** Попробуй выбрать умный путь!»
                """)
    
                if st.button("🔄 Попробовать снова", key="m2_retry"):
                    st.session_state.m2_choice_made = False
                    st.session_state.m2_choice = None
                    st.rerun()
    
            # === УМНЫЙ ПУТЬ ===
            elif "🧠" in choice:
                st.markdown("#### 💬 Ты написал ИИ:")
                with st.chat_message("user"):
                    st.write("Подскажи первый шаг для решения 2x+5=15. "
                             "Не решай за меня!")
    
                with st.chat_message("assistant"):
                    st.markdown("""
                    Отличный подход! 💪 Вот подсказка:
    
                    **Шаг 1:** Перенеси число **+5** на другую сторону 
                    от знака «=». При переносе знак меняется на противоположный!
    
                    > 2x + 5 = 15  
                    > 2x = 15 **- 5**
    
                    Теперь попробуй посчитать, чему равен **2x**?  
                    А потом раздели обе части на **2** — и найдёшь **x**! 🎯
                    """)
    
                st.markdown("---")
    
                st.success("""
                ### 🎓 Ты ПОНЯЛ принцип!
    
                Теперь ты знаешь: чтобы решить уравнение,  
                нужно **перенести числа** и **разделить**.
    
                ⚡ Это работает для ЛЮБОГО уравнения!
                """)
    
                st.info("""
                🐶 Байт: «ВОТ ЭТО по-нашему! 🔥 
                Ты не просто получил ответ — ты получил НАВЫК! 
                Теперь любое уравнение тебе по зубам!»
                """)
    
                if not st.session_state.mission_2_done:
                    add_xp(30)
                    add_badge("🧠 Мозг")
                    st.session_state.mission_2_done = True
    
                st.success(f"🎉 **+30 XP!** Бейдж: 🧠 Мозг! "
                           f"Текущий XP: {st.session_state.xp}")
    
        # Мораль
        if st.session_state.mission_2_done:
            st.markdown("---")
            st.markdown("""
            > ### 📌 Правило Агента:
            > **ИИ = репетитор, а не решала.**  
            > Проси ОБЪЯСНИТЬ, а не решить.  
            > Тогда ты сам станешь умнее! 🧠
            """)
    
    
    # ============================================================
    # МИССИЯ 3: МОЗГОВОЙ ШТУРМ
    # ============================================================
    def page_mission_3():
        """Миссия 3 — Генерация идей через итеративный диалог"""
    
        st.markdown("""
        <div class="mission-header">
            <h2>💡 Миссия 3: Мозговой штурм</h2>
            <p>🐶 Байт: «ИИ — крутой напарник для мозгового штурма! 
            Но если дашь ему скучный запрос — получишь скучные идеи.»</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("""
        ### 📝 Ситуация:
        Учитель биологии задал **проект на свободную тему**.  
        Нужно придумать интересную тему. Давай попросим ИИ!
        """)
    
        st.markdown("---")
    
        step = st.session_state.m3_step
    
        # --- ШАГ 0: Скучный запрос ---
        if step == 0:
            st.markdown("#### 💬 Чат с ИИ-помощником:")
    
            st.info("🐶 Байт: «Начни с простого запроса. "
                    "Посмотрим, что получится...»")
    
            if st.button("📨 Отправить: «Дай темы для проекта по биологии»",
                         type="primary", use_container_width=True, key="m3_step0"):
                st.session_state.m3_step = 1
                st.rerun()
    
        # --- ШАГ 1: Скучные темы ---
        elif step == 1:
            st.markdown("#### 💬 Чат с ИИ-помощником:")
    
            with st.chat_message("user"):
                st.write("Дай темы для проекта по биологии")
    
            with st.chat_message("assistant"):
                st.markdown("""
                Вот темы для проекта по биологии:
                1. 🌱 Строение клетки
                2. 🐸 Земноводные и их среда обитания
                3. 🌳 Фотосинтез и его значение
                4. 🦠 Бактерии в жизни человека
                5. 🧬 Основы генетики
                """)
    
            st.markdown("---")
            st.warning("""
            🐶 Байт: «Хмм... Темы нормальные, но СКУЧНЫЕ. 😴 
            Как из учебника.  
    
            **Секрет крутого промпта:** добавь СВОИ интересы!  
            ИИ не знает, что тебе нравится, пока ты не скажешь!»
            """)
    
            st.markdown("#### Что ответишь?")
    
            col1, col2 = st.columns(2)
            with col1:
                if st.button("😐 «Ну дай ещё темы»",
                             use_container_width=True, key="m3_boring"):
                    st.session_state.m3_step = 2
                    st.rerun()
            with col2:
                if st.button("🔥 «Я люблю видеоигры! Дай темы на стыке "
                             "игр и биологии»",
                             use_container_width=True, key="m3_cool",
                             type="primary"):
                    st.session_state.m3_step = 3
                    st.rerun()
    
        # --- ШАГ 2: Снова скучные ---
        elif step == 2:
            st.markdown("#### 💬 Чат с ИИ-помощником:")
    
            with st.chat_message("user"):
                st.write("Дай темы для проекта по биологии")
            with st.chat_message("assistant"):
                st.write("1. Строение клетки 2. Земноводные 3. Фотосинтез...")
            with st.chat_message("user"):
                st.write("Ну дай ещё темы")
            with st.chat_message("assistant"):
                st.markdown("""
                Ещё темы:
                1. 🌊 Экосистема океана
                2. 🐝 Роль пчёл в природе
                3. 🍄 Грибы: растения или нет?
                """)
    
            st.error("""
            🐶 Байт: «Опять то же самое! 😩  
            ИИ не умеет читать мысли.  
            Если не скажешь, что тебе интересно —  
            он будет выдавать одинаковые ответы бесконечно.  
    
            Давай попробуем по-другому!»
            """)
    
            if st.button("🔥 Окей, скажу про видеоигры!",
                         type="primary", use_container_width=True, key="m3_fix"):
                st.session_state.m3_step = 3
                st.rerun()
    
        # --- ШАГ 3: Крутые темы ---
        elif step == 3:
            st.markdown("#### 💬 Чат с ИИ-помощником:")
    
            with st.chat_message("user"):
                st.write("Дай темы для проекта по биологии")
            with st.chat_message("assistant"):
                st.write("1. Строение клетки 2. Земноводные 3. Фотосинтез...")
    
            with st.chat_message("user"):
                st.write("Я обожаю видеоигры! 🎮 Придумай темы "
                         "на стыке видеоигр и биологии. "
                         "Что-нибудь необычное и крутое!")
    
            with st.chat_message("assistant"):
                st.markdown("""
                О, теперь СОВСЕМ другое дело! 🔥 Лови:
    
                1. 🐉 **Биомеханика монстров в играх**  
                   Могут ли драконы из Skyrim летать с точки зрения физики и биологии?
    
                2. 🧟 **Зомби-вирус: наука vs фантазия**  
                   Какие реальные паразиты управляют поведением хозяина? (Спойлер: грибок кордицепс из The Last of Us реален!)
    
                3. 🌿 **Майнкрафт-ферма vs реальная ферма**  
                   Сравнение виртуального и реального выращивания растений
    
                4. 🧬 **Покемоны и эволюция**  
                   Как работает эволюция в играх и в реальной природе
    
                5. 🤖 **Может ли человек стать киборгом?**  
                   Реальные бионические протезы и апгрейды из игр
                """)
    
            st.markdown("---")
            st.success("""
            ### 🎉 ВОТ ЭТО ТЕМЫ!  
    
            Видишь разницу? Одно слово «видеоигры» — и ИИ выдал  
            идеи, от которых учитель упадёт со стула! 😲
            """)
    
            if not st.session_state.mission_3_done:
                add_xp(30)
                add_badge("💡 Генератор идей")
                st.session_state.mission_3_done = True
    
            st.success(f"🎉 **+30 XP!** Бейдж: 💡 Генератор идей! "
                       f"Текущий XP: {st.session_state.xp}")
    
            st.markdown("""
            > ### 📌 Правило Агента:
            > **Добавляй свои интересы в промпт!**  
            > ИИ не умеет читать мысли.  
            > Чем больше контекста — тем круче результат! 🎯
            """)
    
    
    # ============================================================
    # МИССИЯ 4: УКРОТИТЕЛЬ ГАЛЛЮЦИНАЦИЙ
    # ============================================================
    def page_mission_4():
        """Миссия 4 — Научиться распознавать ошибки ИИ"""
    
        st.markdown("""
        <div class="mission-header">
            <h2>🔍 Миссия 4: Укротитель Галлюцинаций</h2>
            <p>🐶 Байт: «Галлюцинация — это когда ИИ врёт, 
            но делает это ОЧЕНЬ уверенно. 
            Как одноклассник, который не учил, но отвечает у доски!»</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("""
        ### 🕵️ Задание:  
        ИИ написал историческую справку. Но в ней спрятана **чушь**!  
        Найди её, используя инструменты детектива.
        """)
    
        st.markdown("---")
    
        # Текст с ошибкой
        st.markdown("""
        ### 📜 Текст от ИИ:
    
        > **Битва при Ватерлоо (1815 год)**
        > 
        > Наполеон Бонапарт, великий французский полководец,  
        > потерпел сокрушительное поражение в битве при Ватерлоо.  
        > 
        > Главной причиной его проигрыша стало то, что  
        > **у Наполеона разрядился смартфон** 📱, и он не смог  
        > вовремя отправить приказы своим генералам через  
        > мессенджер. Связь прервалась в самый ответственный  
        > момент, и войска действовали несогласованно.
        > 
        > Это привело к победе герцога Веллингтона  
        > и окончательному падению Наполеона.
        """)
    
        st.markdown("---")
    
        if not st.session_state.m4_choice_made:
            st.markdown("### 🧰 Инструменты детектива:")
            st.markdown("Что ты сделаешь с этим текстом?")
    
            col1, col2, col3 = st.columns(3)
    
            with col1:
                if st.button("✅ Поверить\n\n«Звучит логично!»",
                             use_container_width=True, key="m4_believe"):
                    st.session_state.m4_choice_made = True
                    st.session_state.m4_choice = "believe"
                    st.rerun()
    
            with col2:
                if st.button("🤔 «А ты уверен?»\n\nПереспросить ИИ",
                             use_container_width=True, key="m4_doubt"):
                    st.session_state.m4_choice_made = True
                    st.session_state.m4_choice = "doubt"
                    st.rerun()
    
            with col3:
                if st.button("📋 «Докажи!»\n\nПотребовать источники",
                             use_container_width=True, key="m4_prove",
                             type="primary"):
                    st.session_state.m4_choice_made = True
                    st.session_state.m4_choice = "prove"
                    st.rerun()
    
        else:
            choice = st.session_state.m4_choice
    
            # === ПОВЕРИТЬ — ПРОВАЛ ===
            if choice == "believe":
                st.error("""
                ### ❌ ПРОВАЛ ДЕТЕКТИВА!
    
                Ты поверил, что у Наполеона в 1815 году  
                был **СМАРТФОН**?! 📱😱
    
                Смартфоны изобрели только в 2007 году!  
                Наполеон жил за 200 лет до этого!
    
                ИИ написал полную чушь, но звучало убедительно, правда?  
                Это и есть **галлюцинация ИИ** — уверенное враньё.
                """)
    
                st.warning("🐶 Байт: «Не расстраивайся! "
                           "На это попадаются даже взрослые. "
                           "Главное — теперь ты знаешь, "
                           "что ИИ МОЖЕТ врать!»")
    
                if st.button("🔄 Попробовать снова",
                             use_container_width=True, key="m4_retry"):
                    st.session_state.m4_choice_made = False
                    st.session_state.m4_choice = None
                    st.rerun()
    
            # === ПЕРЕСПРОСИТЬ — ПОЛУПОБЕДА ===
            elif choice == "doubt":
                st.warning("""
                ### 🤔 Неплохо, но недостаточно!
                """)
    
                with st.chat_message("user"):
                    st.write("А ты уверен насчёт смартфона?")
    
                with st.chat_message("assistant"):
                    st.markdown("""
                    Да, я уверен! Наполеон использовал  
                    передовые технологии своего времени  
                    для управления армией... 
    
                    *(ИИ продолжает настаивать на своём)*
                    """)
    
                st.warning("""
                🐶 Байт: «Видишь? ИИ не всегда признаёт ошибки,  
                если просто переспросить.  
                Нужно требовать **ДОКАЗАТЕЛЬСТВА и ИСТОЧНИКИ**!  
                Попробуй кнопку "Докажи!"»
                """)
    
                if st.button("📋 Потребовать доказательства!",
                             type="primary", use_container_width=True,
                             key="m4_retry_prove"):
                    st.session_state.m4_choice = "prove"
                    st.rerun()
    
            # === ДОКАЖИ — ПОБЕДА ===
            elif choice == "prove":
                st.success("### 🏆 ОТЛИЧНАЯ РАБОТА, ДЕТЕКТИВ!")
    
                with st.chat_message("user"):
                    st.write("Стоп! Докажи, что у Наполеона был смартфон. "
                             "Дай ссылку на источник!")
    
                with st.chat_message("assistant"):
                    st.markdown("""
                    😅 Прошу прощения! Вы правы, это ошибка.
    
                    **Исправленная версия:**
    
                    Наполеон проиграл битву при Ватерлоо по нескольким причинам:
                    - 🌧️ Сильный дождь накануне — пушки застревали в грязи
                    - ⏰ Маршал Груши опоздал с подкреплением
                    - 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Войска Веллингтона и Блюхера объединились
    
                    Никаких смартфонов в 1815 году, конечно, не было!  
                    Приказы передавали через конных посыльных. 🐴
                    """)
    
                st.markdown("---")
    
                if not st.session_state.mission_4_done:
                    add_xp(30)
                    add_badge("🔍 Детектив правды")
                    st.session_state.mission_4_done = True
    
                st.success(f"🎉 **+30 XP!** Бейдж: 🔍 Детектив правды! "
                           f"Текущий XP: {st.session_state.xp}")
    
                st.markdown("""
                > ### 📌 Правило Агента:
                > **Всегда проверяй факты от ИИ!**  
                > Требуй источники. Гугли. Спрашивай учителя.  
                > ИИ звучит умно, но может нести полную чушь! 🤥
                """)
    
    
    # ============================================================
    # МИССИЯ 5: ИИ-ПЕРЕВОДЧИК (ТРАНСФОРМАТОР ТЕКСТА)
    # ============================================================
    def page_mission_5():
        """Миссия 5 — Превращение сложного текста в понятный"""
    
        st.markdown("""
        <div class="mission-header">
            <h2>🔮 Миссия 5: ИИ-Переводчик</h2>
            <p>🐶 Байт: «Самая крутая суперсила ИИ — 
            превращать заумную муть в понятный текст! 
            Давай попробуем!»</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("""
        ### 📖 Вот текст из учебника биологии:
        """)
    
        st.error("""
        > **Фотосинтез** — это процесс образования органических веществ 
        > из углекислого газа и воды на свету при участии 
        > фотосинтетических пигментов (хлорофилл у растений, 
        > бактериохлорофилл у бактерий). В ходе световой фазы 
        > фотосинтеза происходит фотолиз воды с выделением 
        > молекулярного кислорода, а в темновой фазе — 
        > фиксация CO₂ в цикле Кальвина с образованием глюкозы.
        """)
    
        st.markdown("""
        😵 Ничего не понятно, правда?  
    
        Выбери **«линзу»** — способ, которым ИИ перескажет этот текст:
        """)
    
        st.markdown("---")
    
        # Выбор "линзы"
        col1, col2, col3 = st.columns(3)
    
        with col1:
            rapper = st.button("🎤 Объясни\nкак рэпер",
                               use_container_width=True, key="m5_rapper")
        with col2:
            minecraft = st.button("⛏️ Объясни через\nМайнкрафт",
                                  use_container_width=True, key="m5_mc")
        with col3:
            baby = st.button("👶 Объясни\n5-летнему",
                             use_container_width=True, key="m5_baby")
    
        # Обработка нажатий
        if rapper:
            st.session_state.m5_lens = "rapper"
            st.session_state.m5_transformed = True
        elif minecraft:
            st.session_state.m5_lens = "minecraft"
            st.session_state.m5_transformed = True
        elif baby:
            st.session_state.m5_lens = "baby"
            st.session_state.m5_transformed = True
    
        # Показ результата
        if st.session_state.m5_transformed and st.session_state.m5_lens:
            st.markdown("---")
            lens = st.session_state.m5_lens
    
            if lens == "rapper":
                st.success("### 🎤 Версия для рэпера:")
                st.markdown("""
                > *Йо, слушай сюда, я расскажу про фотосинтез, бро!* 🎵
                > 
                > *Растение стоит, ловит свет — это его хлеб!*  
                > *Берёт воду из корней, CO₂ из воздуха — респект!*  
                > *Хлорофилл — это зелень, это пигмент, это стиль,*  
                > *Он ловит фотоны, как DJ ловит бит!*  
                > 
                > *Вода расщепляется — кислород на выход, йоу!*  
                > *А из углекислого газа — глюкоза, это фуд!*  
                > *Растение само себе готовит еду,*  
                > *Без доставки, без кухни — просто стоит на свету!* 🌱🔥
                > 
                > *Дроп!* 🎤⬇️
                """)
    
            elif lens == "minecraft":
                st.success("### ⛏️ Версия через Майнкрафт:")
                st.markdown("""
                > Представь, что растение — это **автоматическая ферма** 
                > в Майнкрафте! ⛏️
                > 
                > 🌞 **Солнечный свет** = редстоун-энергия, которая 
                > запускает всю систему
                > 
                > 💧 **Вода** = один ресурс на входе 
                > (как вода в ферме пшеницы)
                > 
                > 💨 **CO₂ (углекислый газ)** = второй ресурс 
                > (берётся из воздуха, как будто из воздуха крафтится)
                > 
                > 🟢 **Хлорофилл** = механизм крафта 
                > (зелёная штука в листьях, как верстак)
                > 
                > 📦 **На выходе:**
                > - 🍬 **Глюкоза** (сахар) = еда для растения, как хлеб для игрока
                > - 💨 **Кислород** = побочный продукт, но нам он ОЧЕНЬ нужен для дыхания!
                > 
                > По сути, растение — это **крафтер**, который из воды и воздуха 
                > делает еду, используя солнце как источник энергии! 🌱✨
                """)
    
            elif lens == "baby":
                st.success("### 👶 Версия для 5-летнего:")
                st.markdown("""
                > Смотри, малыш! 🌻
                > 
                > Цветочек хочет кушать. Но он же не может 
                > пойти в холодильник, правда? 
                > 
                > Поэтому он сам себе готовит еду! 🍳
                > 
                > Он берёт **водичку** из земли 💧  
                > И **воздух** 💨  
                > А потом включает **солнышко** как лампочку ☀️  
                > 
                > И — БАМ! — получается **сахарок**! 🍬  
                > Это его обед!
                > 
                > А ещё он выпускает **воздух, которым мы дышим**!  
                > Спасибо, цветочек! 🌸❤️
                > 
                > Вот и весь фотосинтез! Просто, правда? 😊
                """)
    
            # Начисление XP и бейджа
            if not st.session_state.mission_5_done:
                add_xp(40)
                add_badge("🔮 Нейро-Мастер")
                st.session_state.mission_5_done = True
    
            st.success(f"🎉 **+40 XP!** Бейдж: 🔮 Нейро-Мастер! "
                       f"Текущий XP: {st.session_state.xp}")
    
            # Кнопки для переключения линз
            st.markdown("---")
            st.info("💡 Попробуй другие линзы — текст изменится!")
    
            st.markdown("""
            > ### 📌 Правило Агента:
            > **ИИ — лучший переводчик со «сложного» на «понятный»!**  
            > Не понимаешь тему? Попроси ИИ объяснить:
            > - Через твоё хобби 🎮
            > - Простыми словами 👶  
            > - С примерами из жизни 🌍
            """)
    
    
    # ============================================================
    # ФИНАЛЬНЫЙ ЭКРАН
    # ============================================================
    def page_finale():
        """Поздравительный экран при достижении 150 XP"""
    
        st.balloons()
    
        st.markdown('<p class="cyber-title">🏆 ПОЗДРАВЛЯЕМ! 🏆</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="cyber-subtitle">Ты прошёл все миссии!</p>',
                    unsafe_allow_html=True)
    
        st.markdown("---")
    
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ### 🤖 Байт говорит:
    
            > *«Вау! Ты набрал **150 XP** и стал настоящим  
            > **Нейро-Мастером**! 🎓*
            > 
            > *Теперь ты знаешь:*
            > 
            > *✅ Как составить идеальный промпт*  
            > *✅ Почему ИИ — репетитор, а не решала*  
            > *✅ Как генерировать крутые идеи*  
            > *✅ Как ловить ИИ на вранье*  
            > *✅ Как превращать сложное в простое*  
            > 
            > *Ты готов к будущему! 🚀*  
            > *Используй ИИ с умом — и он станет  
            > твоим лучшим напарником!»* 🐶✨
            """)
    
        st.markdown("---")
    
        # Все бейджи
        st.markdown("### 🏅 Твои бейджи:")
        if st.session_state.badges:
            badge_cols = st.columns(len(st.session_state.badges))
            for i, badge in enumerate(st.session_state.badges):
                with badge_cols[i]:
                    st.markdown(f"""
                    <div class="badge-card" style="font-size: 1.1rem;">
                        {badge}
                    </div>
                    """, unsafe_allow_html=True)
    
        st.markdown("---")
    
        # Кодекс
        st.markdown("""
        ### 📜 Кодекс Нейро-Мастера:
    
        | # | Правило | 
        |---|---------|
        | 1 | 🎭 **Роль + Задача + Формат** = крутой промпт |
        | 2 | 🧠 Проси **объяснить**, а не решить |
        | 3 | 💡 Добавляй **свои интересы** в запрос |
        | 4 | 🔍 **Проверяй факты** — ИИ может врать |
        | 5 | 🔮 Используй ИИ как **переводчик** сложного |
        """)
    
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Пройти заново!", use_container_width=True,
                         type="primary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    
    # ============================================================
    # ГЛАВНЫЙ РОУТЕР
    # ============================================================
    def main():
        """Основная логика маршрутизации приложения"""
    
        # Рендерим сайдбар
        render_sidebar()
    
        # Проверяем, не достиг ли пользователь максимума XP
        if (st.session_state.xp >= st.session_state.max_xp
                and not st.session_state.finale_shown):
            st.session_state.finale_shown = True
    
        # Если финал — показываем его принудительно (один раз)
        if st.session_state.finale_shown and st.session_state.current_page != "home":
            # Показываем финал только если все миссии пройдены
            all_done = all([
                st.session_state.mission_1_done,
                st.session_state.mission_2_done,
                st.session_state.mission_3_done,
                st.session_state.mission_4_done,
                st.session_state.mission_5_done,
            ])
            if all_done:
                page_finale()
                return
    
        # Роутинг по страницам
        page = st.session_state.current_page
    
        if page == "home":
            page_home()
        elif page == "mission_1":
            page_mission_1()
        elif page == "mission_2":
            page_mission_2()
        elif page == "mission_3":
            page_mission_3()
        elif page == "mission_4":
            page_mission_4()
        elif page == "mission_5":
            page_mission_5()
        else:
            page_home()
    main()
  


# ==========================================
# Главная логика навигации
# ==========================================

# Инициализация состояния
if "current_app" not in st.session_state:
    st.session_state.current_app = None

def go_to_app(app_name):
    st.session_state.current_app = app_name

def go_home():
    st.session_state.current_app = None


# Если выбрано приложение — показываем его
if st.session_state.current_app:
    # Кнопка "Назад"
    if st.button("⬅️ Вернуться на дорогу", key="back_btn"):
        go_home()
        st.rerun()
    
    st.markdown("---")
    
    # Роутинг
    apps = {
        "calculator": app_calculator,
        "todo": app_todo,
        "notes": app_notes,
        "weather": app_weather,
    }
    
    app_func = apps.get(st.session_state.current_app)
    if app_func:
        app_func()

else:
    # ==========================================
    # Главная страница — ДОРОГА
    # ==========================================
    
    st.markdown('<div class="main-title">🛤️ Дорога приложений</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Выберите остановку на пути</div>', unsafe_allow_html=True)
    
    # Визуализация дороги
    road_apps = [
        {"id": "calculator", "icon": "🧮", "name": "Дерево решений", "desc": "Как работает ИИ", "color": "#4CAF50"},
        {"id": "todo", "icon": "✅", "name": "ИИ-патруль", "desc": "Как обманывает ИИ", "color": "#2196F3"},
        {"id": "notes", "icon": "📝", "name": "Фото", "desc": "Найди дипфейк", "color": "#FF9800"},
        {"id": "weather", "icon": "🌤️", "name": "Промпты", "desc": "Научись писать промпты", "color": "#9C27B0"},
    ]
    
    # Рисуем дорогу
    for i, app in enumerate(road_apps):
        # Сегмент дороги перед кнопкой
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: flex-end; height: 100px;">
                    <div style="width: 3px; height: 100%; background: 
                    repeating-linear-gradient(to bottom, #FFD700 0px, #FFD700 10px, transparent 10px, transparent 20px);
                    margin-right: 20px;"></div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, {app['color']}CC, {app['color']}99); 
                padding: 15px; border-radius: 15px; text-align: center; color: white;
                border: 3px solid {app['color']}; margin: 5px 0;">
                    <div style="font-size: 2.5em;">{app['icon']}</div>
                    <div style="font-size: 1.3em; font-weight: bold;">{app['name']}</div>
                    <div style="font-size: 0.9em; opacity: 0.9;">{app['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"🚪 Открыть {app['name']}", key=f"road_btn_{app['id']}", use_container_width=True):
                go_to_app(app["id"])
                st.rerun()
        
        with col3:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: flex-start; height: 100px;">
                    <div style="font-size: 1.5em; margin-left: 20px; opacity: 0.5;">
                        📍 Остановка {i + 1}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Разделитель дороги между кнопками
        if i < len(road_apps) - 1:
            st.markdown(
                """
                <div style="display: flex; justify-content: center; margin: 0;">
                    <div style="width: 8px; height: 60px; background: 
                    repeating-linear-gradient(to bottom, #FFD700 0px, #FFD700 8px, transparent 8px, transparent 16px);
                    border-left: 30px solid #555; border-right: 30px solid #555;">
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Конец дороги
    st.markdown(
        """
        <div style="text-align: center; margin-top: 20px; padding: 20px;">
            <div style="font-size: 2em;">🏁</div>
            <div style="color: #888; font-size: 1.1em;">Конец дороги</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Футер
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; padding: 10px;">
            <p>🛤️ Дорога приложений — выберите свою остановку!</p>
        </div>
        """,
        unsafe_allow_html=True
    )
