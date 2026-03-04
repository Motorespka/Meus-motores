# --- NOVO SISTEMA DE ANÁLISE TÉCNICA ---
            if st.session_state.get(f"sc_{idx}"):
                st.markdown("---")
                st.subheader("⚙️ Análise de Viabilidade Técnica")
                
                # Input para o usuário simular o que vai usar
                fio_simulado = st.text_input("Qual fio você pretende usar?", key=f"input_sim_{idx}", placeholder="Ex: 2x18")
                
                if fio_simulado:
                    area_orig = calcular_area_mm2(row['Fio_Principal'])
                    area_nova = calcular_area_mm2(fio_simulado)
                    
                    if area_orig > 0:
                        diff = ((area_nova - area_orig) / area_orig) * 100
                        
                        # Cálculos de Variáveis Extras (Lógica Técnica)
                        # 1. Densidade de Corrente Estimada
                        aquecimento = "NORMAL" if diff >= -2 else "ALTO (Risco de fumaça)" if diff < -7 else "MODERADO"
                        # 2. Perda de Torque
                        torque = "MANTIDO" if diff >= -3 else "REDUZIDO"
                        
                        # Dashboard de Comparação
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Área Original", f"{area_orig:.3f} mm²")
                        c2.metric("Área Nova", f"{area_nova:.3f} mm²", f"{diff:.2f}%")
                        c3.metric("Aquecimento", aquecimento, delta_color="inverse" if diff < 0 else "normal")

                        # Alerta Visual estilo Semáforo
                        if -3.0 <= diff <= 5.0:
                            st.success(f"✅ **VIÁVEL:** A bitola {fio_simulado} substitui bem o fio {row['Fio_Principal']}. O motor manterá o torque original.")
                        elif -8.0 <= diff < -3.0:
                            st.warning(f"⚠️ **ATENÇÃO:** Redução de cobre detectada. O motor pode esquentar mais que o normal em carga máxima.")
                        else:
                            st.error(f"🚨 **PERIGO:** Diferença de {diff:.2f}%. Risco alto de queima imediata ou perda total de força.")
                        
                        # Sugestões rápidas automáticas para ajudar a decidir
                        st.write("**Opções equivalentes encontradas:**")
                        sugest = gerar_sugestoes(area_orig)
                        cols_sug = st.columns(3)
                        for i, s in enumerate(sugest[:3]):
                            with cols_sug[i]:
                                st.markdown(f"""
                                    <div style="background:{s['cor']}; color:white; padding:5px; border-radius:5px; text-align:center;">
                                        {s['fio']}< title="Diferença: {s['diff']:.1f}%">
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("O Fio Principal original não foi reconhecido para cálculo.")
                else:
                    st.info("Digite a bitola que você quer testar no campo acima para ver se o motor aguenta.")
