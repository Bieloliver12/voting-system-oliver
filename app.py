import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# Configuration
VOTES_FILE = "votes.json"
USERS_FILE = "users.json"

# Valid users with their IDs and names
VALID_USERS = {
    "43483736M": "Gabriel Oliver",
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

# Candidates for president
CANDIDATES = [
    "Gabriel Oliver",
    "Gonzalo Ros", 
    "Oscar Boado",
    "Pablo Beaus"
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
            files_deleted.append("votes.json")
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)
            files_deleted.append("users.json")
        
        return len(files_deleted) > 0
    except Exception as e:
        st.error(f"Error deleting files: {str(e)}")
        return False

def can_vote_for_candidate(user_id, candidate):
    """Check if user can vote for this candidate (can't vote for themselves)"""
    user_name = VALID_USERS.get(user_id, "")
    return user_name != candidate

def get_results():
    """Get voting results"""
    votes = load_votes()
    results = {candidate: 0 for candidate in CANDIDATES}
    
    for vote in votes.values():
        candidate = vote.get("candidate")
        if candidate in results:
            results[candidate] += 1
    
    return results

def main():
    st.set_page_config(
        page_title="Voting System - Soluciones Digitales Oliver",
        page_icon="🗳️",
        layout="centered"
    )
    
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
    st.title("🗳️ Sistema de Votación")
    st.subheader("Elección Presidente - Soluciones Digitales Oliver")
    st.markdown("---")

    # Check if user wants to see results (admin only)
    if st.sidebar.button("Ver Resultados (Solo Admin)"):
        st.session_state.show_results = True
        st.session_state.authenticated = False
        st.session_state.confirm_delete = False

    # Results page (Admin only)
    if st.session_state.show_results:
        st.header("🔐 Acceso a Resultados")
        
        admin_id = st.text_input("Ingrese su ID para ver los resultados:", key="admin_login")
        
        if st.button("Acceder a Resultados"):
            if admin_id == ADMIN_ID:
                # Set session state to stay in results view
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ ID no válido o sin permisos para ver resultados.")
        
        # Only show results if admin is logged in
        if st.session_state.get('admin_logged_in', False):
            st.success(f"Bienvenido, {VALID_USERS[ADMIN_ID]}")
            
            # Show results
            st.header("📊 Resultados de la Votación")
            
            results = get_results()
            total_votes = sum(results.values())
            
            if total_votes > 0:
                # Create results dataframe
                df_results = pd.DataFrame([
                    {"Candidato": candidate, "Votos": votes, "Porcentaje": f"{(votes/total_votes)*100:.1f}%"}
                    for candidate, votes in sorted(results.items(), key=lambda x: x[1], reverse=True)
                ])
                
                st.dataframe(df_results, use_container_width=True)
                
                # Show bar chart
                st.bar_chart(results)
                
                st.metric("Total de Votos", total_votes)
                
                # Show winner
                winner = max(results.items(), key=lambda x: x[1])
                if winner[1] > 0:
                    st.success(f"🏆 Ganador actual: **{winner[0]}** con {winner[1]} votos")
                
                # Admin button to clear all votes
                st.markdown("---")
                st.subheader("🗑️ Administración")
                
                if not st.session_state.confirm_delete:
                    if st.button("🚨 BORRAR TODOS LOS VOTOS", type="secondary"):
                        st.session_state.confirm_delete = True
                        st.rerun()
                else:
                    st.warning("⚠️ ¿Está seguro de borrar TODOS los votos? Esta acción no se puede deshacer.")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✅ SÍ, BORRAR TODO", type="primary"):
                            if clear_all_votes():
                                st.session_state.confirm_delete = False
                                st.success("🗑️ Todos los votos han sido borrados.")
                                st.rerun()
                            else:
                                st.error("No se pudieron borrar los archivos.")
                    with col2:
                        if st.button("❌ Cancelar"):
                            st.session_state.confirm_delete = False
                            st.rerun()
            else:
                st.info("No hay votos registrados aún.")
                
                # Admin button to clear all votes (even when no votes)
                st.markdown("---")
                st.subheader("🗑️ Administración")
                if st.button("🚨 RESETEAR SISTEMA", type="secondary"):
                    if clear_all_votes():
                        st.success("🗑️ Sistema reseteado.")
                        st.rerun()
                    else:
                        st.info("No había archivos para borrar.")
        
        if st.button("← Volver al Login"):
            st.session_state.show_results = False
            st.session_state.confirm_delete = False
            st.rerun()
        
        return

    # Login page
    if not st.session_state.authenticated:
        st.header("🔐 Identificación de Usuario")
        st.write("Ingrese su ID para acceder al sistema de votación:")
        
        user_id = st.text_input("ID de Usuario:", placeholder="Ej: 43484746M")
        
        if st.button("🚀 Ingresar", type="primary"):
            if user_id in VALID_USERS:
                if has_user_voted(user_id):
                    st.error("❌ Ya has votado. Solo se permite un voto por persona.")
                else:
                    st.session_state.authenticated = True
                    st.session_state.user_id = user_id
                    st.session_state.user_name = VALID_USERS[user_id]
                    st.success(f"✅ Bienvenido/a, {VALID_USERS[user_id]}")
                    st.rerun()
            else:
                st.error("❌ ID no válido. Por favor, verifique su ID.")
        
        st.markdown("---")
        st.info("💡 **Instrucciones:**\n- Ingrese su ID exactamente como se le proporcionó\n- Solo puede votar una vez\n- Su voto será completamente anónimo")
        
    # Voting page
    else:
        st.header(f"👋 Hola, {st.session_state.user_name}")
        st.subheader("🗳️ Seleccione su candidato para Presidente")
        
        # Get available candidates (filter out self if user is a candidate)
        user_name = st.session_state.user_name
        available_candidates = [c for c in CANDIDATES if c != user_name]
        
        if not available_candidates:
            st.error("❌ No puede votar ya que usted es el único candidato.")
            if st.button("🚪 Cerrar Sesión"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.rerun()
            return
        
        if len(available_candidates) < len(CANDIDATES):
            st.info(f"ℹ️ Nota: No puede votar por usted mismo ({user_name})")
        
        # Check if user just voted
        if st.session_state.vote_submitted:
            # Show success message and balloons
            st.success(f"🎉 ¡Voto registrado exitosamente por {st.session_state.voted_candidate}!")
            st.balloons()
            st.info("Gracias por participar. Presione 'Continuar' para salir.")
            
            if st.button("✅ Continuar", type="primary"):
                # Reset all session state
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.vote_submitted = False
                st.session_state.voted_candidate = None
                st.success("✅ Sesión cerrada. Ya no puede votar de nuevo.")
                st.rerun()
            
            # Don't show the voting form if vote was just submitted
            return
        
        st.markdown("**Candidatos disponibles:**")
        
        # Voting form
        with st.form("voting_form"):
            selected_candidate = st.radio(
                "Seleccione un candidato:",
                available_candidates,
                index=None
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                vote_button = st.form_submit_button("✅ Emitir Voto", type="primary")
            
            with col2:
                logout_button = st.form_submit_button("🚪 Cerrar Sesión")
        
        if vote_button:
            if selected_candidate:
                # Save vote immediately
                if save_vote(st.session_state.user_id, selected_candidate):
                    # Set session state to show success page
                    st.session_state.vote_submitted = True
                    st.session_state.voted_candidate = selected_candidate
                    st.rerun()
                else:
                    st.error("Error al guardar el voto. Inténtelo de nuevo.")
            else:
                st.error("❌ Por favor, seleccione un candidato antes de votar.")
        
        if logout_button:
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.rerun()
        
        st.markdown("---")
        st.info("🔒 **Su voto es completamente anónimo y seguro**")

if __name__ == "__main__":
    main()