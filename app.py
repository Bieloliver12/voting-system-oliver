import streamlit as st
import json
import os
from datetime import datetime, time
import pandas as pd
import pytz
import time as time_module

# Configuration
VOTES_FILE = "votes_runoff.json"
USERS_FILE = "users_runoff.json"

# Valid users with their IDs and names
VALID_USERS = {
    "43483736M": "Gabriel Oliver",  # Corrected ID
    "41607985L": "Ricky Ortiz", 
    "48126919V": "Gonzalo Ros",
    "23899839X": "Oscar Boado",
    "39974093R": "Tillo",
    "46151901D": "Miguel Ginot",
    "21773570E": "Pablo Beaus",
    "46152551S": "Carlos Oteiza",
    "23929566K": "Ignacio Garcia",
    "26271508B": "Pablo Corbat"
}

# RUNOFF CANDIDATES - Only the two finalists
RUNOFF_CANDIDATES = [
    "Gabriel Oliver",
    "Gonzalo Ros"
]

# Admin user who can see results
ADMIN_ID = "46151901D"  # Miguel Ginot

def load_votes():
    """Load votes from JSON file"""
    if os.path.exists(VOTES_FILE):
        try:
            with open(VOTES_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_vote(user_id, candidate):
    """Save a vote to the JSON file"""
    try:
        votes = load_votes()
        
        # Create anonymous vote entry
        vote_entry = {
            "candidate": candidate,
            "timestamp": datetime.now().isoformat(),
            "vote_id": len(votes) + 1
        }
        
        # Save vote with anonymous ID
        votes[f"vote_{len(votes) + 1}"] = vote_entry
        
        # Also track which users have voted (separate from votes for anonymity)
        voted_users = load_voted_users()
        voted_users.append(user_id)
        save_voted_users(voted_users)
        
        with open(VOTES_FILE, 'w') as f:
            json.dump(votes, f, indent=2)
            
        return True
    except Exception as e:
        st.error(f"Error saving vote: {str(e)}")
        return False

def load_voted_users():
    """Load list of users who have already voted"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_voted_users(voted_users):
    """Save list of users who have voted"""
    with open(USERS_FILE, 'w') as f:
        json.dump(voted_users, f, indent=2)

def has_user_voted(user_id):
    """Check if user has already voted"""
    voted_users = load_voted_users()
    return user_id in voted_users

def clear_all_votes():
    """Clear all votes and reset the system (Admin only)"""
    try:
        files_deleted = []
        if os.path.exists(VOTES_FILE):
            os.remove(VOTES_FILE)
            files_deleted.append("votes_runoff.json")
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)
            files_deleted.append("users_runoff.json")
        
        return len(files_deleted) > 0
    except Exception as e:
        st.error(f"Error deleting files: {str(e)}")
        return False

def get_results():
    """Get voting results"""
    votes = load_votes()
    results = {candidate: 0 for candidate in RUNOFF_CANDIDATES}
    
    for vote in votes.values():
        candidate = vote.get("candidate")
        if candidate in results:
            results[candidate] += 1
    
    return results

def show_results_page():
    """Show the results page (separated for reuse)"""
    # Custom CSS for results page
    st.markdown("""
    <style>
    .results-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
    .results-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .winner-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 10px 25px rgba(245, 87, 108, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="results-header">
        <h1>🔐 Panel de Administración</h1>
        <h3>Segunda Vuelta Electoral</h3>
    </div>
    """, unsafe_allow_html=True)
    
    admin_id = st.text_input("🆔 Ingrese su ID para ver los resultados:", key="admin_login")
    
    if st.button("🚀 Acceder a Resultados", type="primary"):
        if admin_id == ADMIN_ID:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("❌ ID no válido o sin permisos para ver resultados.")
    
    # Only show results if admin is logged in
    if st.session_state.get('admin_logged_in', False):
        st.success(f"✅ Bienvenido, {VALID_USERS[ADMIN_ID]}")
        
        # Show results
        st.markdown("## 📊 Resultados de la Segunda Vuelta")
        
        results = get_results()
        total_votes = sum(results.values())
        
        if total_votes > 0:
            # Create two columns for candidate results
            col1, col2 = st.columns(2)
            
            gabriel_votes = results.get("Gabriel Oliver", 0)
            gonzalo_votes = results.get("Gonzalo Ros", 0)
            
            with col1:
                gabriel_pct = (gabriel_votes/total_votes)*100 if total_votes > 0 else 0
                st.markdown(f"""
                <div class="results-card">
                    <h3>🏛️ Gabriel Oliver</h3>
                    <h2 style="color: #667eea;">{gabriel_votes} votos</h2>
                    <h4>{gabriel_pct:.1f}%</h4>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                gonzalo_pct = (gonzalo_votes/total_votes)*100 if total_votes > 0 else 0
                st.markdown(f"""
                <div class="results-card">
                    <h3>🏛️ Gonzalo Ros</h3>
                    <h2 style="color: #764ba2;">{gonzalo_votes} votos</h2>
                    <h4>{gonzalo_pct:.1f}%</h4>
                </div>
                """, unsafe_allow_html=True)
            
            # Progress bars
            st.markdown("### 📈 Progreso de Votación")
            gabriel_progress = gabriel_votes / max(total_votes, 1)
            gonzalo_progress = gonzalo_votes / max(total_votes, 1)
            
            st.write("**Gabriel Oliver**")
            st.progress(gabriel_progress)
            st.write(f"{gabriel_pct:.1f}% ({gabriel_votes} votos)")
            
            st.write("**Gonzalo Ros**")
            st.progress(gonzalo_progress)
            st.write(f"{gonzalo_pct:.1f}% ({gonzalo_votes} votos)")
            
            # Total votes metric
            st.metric("📊 Total de Votos Emitidos", total_votes)
            
            # Show winner or tie
            if gabriel_votes > gonzalo_votes:
                st.markdown(f"""
                <div class="winner-card">
                    <h1>🏆 GANADOR</h1>
                    <h2>Gabriel Oliver</h2>
                    <h3>{gabriel_votes} votos ({gabriel_pct:.1f}%)</h3>
                    <p>¡Felicidades al nuevo Presidente!</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            elif gonzalo_votes > gabriel_votes:
                st.markdown(f"""
                <div class="winner-card">
                    <h1>🏆 GANADOR</h1>
                    <h2>Gonzalo Ros</h2>
                    <h3>{gonzalo_votes} votos ({gonzalo_pct:.1f}%)</h3>
                    <p>¡Felicidades al nuevo Presidente!</p>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            else:
                st.warning("🤝 **EMPATE** - Se requiere más votación para decidir el ganador")
            
            # Voting participation
            total_eligible = len(VALID_USERS)
            participation_rate = (total_votes / total_eligible) * 100
            st.metric("📊 Participación Electoral", f"{participation_rate:.1f}%", f"{total_votes}/{total_eligible} votantes")
            
        else:
            st.info("📭 No hay votos registrados en la segunda vuelta aún.")
        
        # Admin controls
        st.markdown("---")
        st.markdown("## 🛠️ Controles de Administración")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not st.session_state.get('confirm_delete', False):
                if st.button("🗑️ Resetear Segunda Vuelta", type="secondary"):
                    st.session_state.confirm_delete = True
                    st.rerun()
            else:
                st.error("⚠️ ¿Confirma resetear TODOS los votos de la segunda vuelta?")
                if st.button("✅ SÍ, RESETEAR", type="primary"):
                    if clear_all_votes():
                        st.session_state.confirm_delete = False
                        st.success("🗑️ Segunda vuelta reseteada.")
                        st.rerun()
                    else:
                        st.error("Error al resetear.")
                if st.button("❌ Cancelar"):
                    st.session_state.confirm_delete = False
                    st.rerun()
        
        with col2:
            if st.button("📤 Exportar Resultados"):
                results_data = {
                    "timestamp": datetime.now().isoformat(),
                    "total_votes": total_votes,
                    "results": results,
                    "participation_rate": f"{participation_rate:.1f}%"
                }
                st.download_button(
                    label="💾 Descargar Resultados JSON",
                    data=json.dumps(results_data, indent=2),
                    file_name=f"resultados_segunda_vuelta_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    mime="application/json"
                )
    
    if st.button("🔙 Volver al Sistema de Votación"):
        st.session_state.show_results = False
        st.session_state.admin_logged_in = False
        st.session_state.confirm_delete = False
        st.rerun()

def main():
    st.set_page_config(
        page_title="Segunda Vuelta Electoral - Soluciones Digitales Oliver",
        page_icon="🗳️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for outstanding design
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        animation: slideInDown 0.8s ease-out;
    }
    
    .epic-intro {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        position: relative;
        overflow: hidden;
    }
    
    .epic-intro::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shine 3s infinite;
    }
    
    .epic-intro h1 {
        font-size: 3rem;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        font-weight: 800;
    }
    
    .epic-intro h2 {
        font-size: 2rem;
        margin-bottom: 1.5rem;
        color: #ffd700;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    .epic-intro p {
        font-size: 1.3rem;
        line-height: 1.6;
        margin: 1rem 0;
        color: #f0f8ff;
    }
    
    .runoff-announcement {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 20px rgba(245, 87, 108, 0.3);
        animation: pulse 2s infinite;
    }
    
    .candidate-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 2px solid transparent;
        color: #2c3e50;
    }
    
    .candidate-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    .candidate-card h2 {
        color: #2c3e50 !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .candidate-card p {
        color: #34495e !important;
        font-size: 1.1rem;
    }
    
    .gabriel-card {
        border-left: 5px solid #667eea;
        background: linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%);
    }
    
    .gonzalo-card {
        border-left: 5px solid #764ba2;
        background: linear-gradient(135deg, #f3e5f5 0%, #ffffff 100%);
    }
    
    .login-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        margin: 2rem 0;
        color: #2c3e50;
    }
    
    .login-container h2 {
        color: #667eea !important;
    }
    
    .login-container p {
        color: #34495e !important;
    }
    
    .vote-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 2rem 0;
        box-shadow: 0 10px 25px rgba(79, 172, 254, 0.3);
        animation: bounceIn 1s ease-out;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    @keyframes slideInDown {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    @keyframes bounceIn {
        0% { opacity: 0; transform: scale(0.3); }
        50% { opacity: 1; transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .destiny-text {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
        color: #2c3e50;
        box-shadow: 0 10px 20px rgba(255, 154, 158, 0.3);
    }
    
    .destiny-text h3 {
        color: #8e44ad !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .destiny-text p {
        color: #2c3e50 !important;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'vote_submitted' not in st.session_state:
        st.session_state.vote_submitted = False
    if 'voted_candidate' not in st.session_state:
        st.session_state.voted_candidate = None

    # Header
    st.markdown("""
    <div class="epic-intro">
        <h1>⚡ EL MOMENTO DECISIVO ⚡</h1>
        <h2>🏆 ELIGE A TU LÍDER SUPREMO 🏆</h2>
        <p><strong>El destino de Soluciones Digitales Oliver está en TUS manos.</strong></p>
        <p>Después de una batalla épica que terminó en empate, solo DOS GUERREROS permanecen en pie.</p>
        <p><em>Gabriel Oliver</em> vs <em>Gonzalo Ros</em></p>
        <p>🔥 <strong>UNO SERÁ EL REY. UNO SERÁ EL PRESIDENTE. UNO SERÁ LA LEYENDA.</strong> 🔥</p>
        <p>Tu voto no es solo una elección... <strong>ES LA DECISIÓN QUE MARCARÁ LA HISTORIA.</strong></p>
        <p>💫 El poder está en tus manos. Úsalo sabiamente. 💫</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🗳️ SEGUNDA VUELTA ELECTORAL</h1>
        <h2>Elección Definitiva de Presidente</h2>
        <h3>Soluciones Digitales Oliver</h3>
        <p>La decisión final está en tus manos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Runoff announcement
    st.markdown("""
    <div class="runoff-announcement">
        <h2>🔥 ¡SEGUNDA VUELTA!</h2>
        <p>Tras un empate histórico, los dos candidatos finalistas compiten por la presidencia</p>
        <h3>Gabriel Oliver 🆚 Gonzalo Ros</h3>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar info
    with st.sidebar:
        st.markdown("## 📋 Información de la Segunda Vuelta")
        st.info("""
        **🎯 Solo quedan 2 candidatos:**
        - Gabriel Oliver
        - Gonzalo Ros
        
        **📊 Primera vuelta:** Empate
        **🗳️ Ahora:** Votación decisiva
        **🏆 Ganador:** Mayoría simple
        """)
        
        # Live results preview (if admin)
        if st.session_state.get('admin_logged_in'):
            st.markdown("### 📊 Vista Rápida")
            results = get_results()
            total = sum(results.values())
            if total > 0:
                for candidate, votes in results.items():
                    pct = (votes/total)*100
                    st.metric(candidate, f"{votes} votos", f"{pct:.1f}%")
        
        # Admin access
        if st.button("🔐 Panel Admin"):
            st.session_state.show_results = True
            st.session_state.authenticated = False

    # Results page (Admin only)
    if st.session_state.show_results:
        show_results_page()
        return

    # Login page
    if not st.session_state.authenticated:
        st.markdown("""
        <div class="destiny-text">
            <h3>🌟 EL MOMENTO DE LA VERDAD HA LLEGADO 🌟</h3>
            <p><strong>Ciudadano de Soluciones Digitales Oliver</strong>, el universo conspira para que TÚ seas quien decida el futuro.</p>
            <p>Dos titanes han sobrevivido a la primera batalla. Ahora, solo queda la GUERRA FINAL.</p>
            <p><em>Tu voto es tu espada. Tu decisión es tu escudo. Tu elección será tu legado.</em></p>
            <p>🔥 <strong>¿Estás listo para hacer historia?</strong> 🔥</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="login-container">
            <h2 style="text-align: center; color: #667eea;">🔐 Acceso al Sistema de Votación</h2>
            <p style="text-align: center;">Ingresa tu ID para participar en la segunda vuelta</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_id = st.text_input("🆔 ID de Usuario:", placeholder="Ej: 43483736M", key="user_login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 INGRESAR AL SISTEMA", type="primary", use_container_width=True):
                if user_id in VALID_USERS:
                    if has_user_voted(user_id):
                        st.error("❌ Ya has votado en la segunda vuelta. Solo se permite un voto por persona.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        st.session_state.user_name = VALID_USERS[user_id]
                        st.success(f"✅ Bienvenido/a, {VALID_USERS[user_id]}")
                        time_module.sleep(1)
                        st.rerun()
                else:
                    st.error("❌ ID no válido. Por favor, verifique su ID.")
        
        st.markdown("---")
        st.info("💡 **Instrucciones de la Segunda Vuelta:**\n- Solo Gabriel Oliver y Gonzalo Ros están en competencia\n- Debes elegir uno de los dos candidatos\n- Tu voto es completamente anónimo\n- Solo puedes votar una vez")
        
    # Voting page
    else:
        # Check if user just voted
        if st.session_state.vote_submitted:
            st.markdown(f"""
            <div class="vote-success">
                <h1>🎉 ¡VOTO REGISTRADO!</h1>
                <h2>Has votado por: {st.session_state.voted_candidate}</h2>
                <p>Gracias por participar en esta segunda vuelta histórica</p>
                <p>Tu decisión ayudará a elegir al nuevo Presidente</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.balloons()
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("✅ FINALIZAR VOTACIÓN", type="primary", use_container_width=True):
                    # Reset all session state
                    st.session_state.authenticated = False
                    st.session_state.user_id = None
                    st.session_state.user_name = None
                    st.session_state.vote_submitted = False
                    st.session_state.voted_candidate = None
                    st.success("✅ Sesión cerrada exitosamente.")
                    time_module.sleep(1)
                    st.rerun()
            return
        
        # Welcome message
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    padding: 1.5rem; border-radius: 12px; text-align: center; 
                    color: white; margin: 1rem 0;">
            <h2>👋 Bienvenido/a, {st.session_state.user_name}</h2>
            <p>Tu voto decidirá el futuro de Soluciones Digitales Oliver</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("## 🏛️ Selecciona tu Candidato para Presidente")
        
        # Two-column layout for candidates
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="candidate-card gabriel-card">
                <h2>🏛️ Gabriel Oliver</h2>
                <p style="font-size: 1.2em; color: #667eea !important; font-weight: 600;">Candidato Finalista</p>
                <p style="color: #2c3e50 !important;">Experiencia y liderazgo para el futuro</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="candidate-card gonzalo-card">
                <h2>🏛️ Gonzalo Ros</h2>
                <p style="font-size: 1.2em; color: #764ba2 !important; font-weight: 600;">Candidato Finalista</p>
                <p style="color: #2c3e50 !important;">Innovación y cambio organizacional</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Voting form
        st.markdown("### 🗳️ Emite tu Voto")
        
        with st.form("runoff_voting_form"):
            selected_candidate = st.radio(
                "**Selecciona tu candidato para Presidente:**",
                RUNOFF_CANDIDATES,
                index=None,
                help="Elige cuidadosamente - esta es la votación definitiva"
            )
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                logout_button = st.form_submit_button("🚪 Salir", type="secondary")
            
            with col2:
                vote_button = st.form_submit_button("✅ CONFIRMAR VOTO", type="primary", use_container_width=True)
            
            with col3:
                pass  # Empty column for spacing
        
        if vote_button:
            if selected_candidate:
                with st.spinner("Procesando tu voto..."):
                    time_module.sleep(1)  # Add suspense
                    if save_vote(st.session_state.user_id, selected_candidate):
                        st.session_state.vote_submitted = True
                        st.session_state.voted_candidate = selected_candidate
                        st.rerun()
                    else:
                        st.error("❌ Error al guardar el voto. Inténtelo de nuevo.")
            else:
                st.error("❌ Por favor, selecciona un candidato antes de votar.")
        
        if logout_button:
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.rerun()
        
        # Security notice
        st.markdown("---")
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; 
                    border-left: 4px solid #28a745;">
            <p><strong>🔒 Garantías de Seguridad:</strong></p>
            <ul>
                <li>Tu voto es completamente anónimo</li>
                <li>Los datos están encriptados y seguros</li>
                <li>Solo puedes votar una vez</li>
                <li>Los resultados son auditables</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()