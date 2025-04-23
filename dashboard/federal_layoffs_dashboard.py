with tab1:
    st.markdown("""
    <div class='alt-container'>
    <h4 style="margin-bottom: 0.5rem;">Top Skills at Risk</h4>
    """, unsafe_allow_html=True)

    skill_top_n = st.radio("Select number of top skills", options=[5, 10], horizontal=True)
    top_skills = df_filtered.dropna(subset=['skill', 'estimate_layoff']) \
        .groupby("skill")["estimate_layoff"].sum().reset_index() \
        .sort_values("estimate_layoff", ascending=False).head(skill_top_n)
    top_skills['skill'] = top_skills['skill'].str.title()

    if not top_skills.empty:
        fig_skills = px.bar(top_skills, x="skill", y="estimate_layoff", 
                            title=f"Top {skill_top_n} Skills by Estimated Layoffs in {selected_state}",
                            color="estimate_layoff",
                            color_continuous_scale=px.colors.sequential.Teal)
        fig_skills.update_layout(xaxis_title="Skill", yaxis_title="Layoffs", title_font=dict(size=16))
        st.plotly_chart(fig_skills, use_container_width=True)
    else:
        st.warning("No skill data available for selected state.")

    st.markdown("""
    <h4 style="margin-top: 1.5rem;">Top Occupations at Risk</h4>
    """, unsafe_allow_html=True)

    job_top_n = st.radio("Select number of top occupations", options=[5, 10], horizontal=True)
    top_jobs = df_filtered.dropna(subset=['occupation', 'estimate_layoff']) \
        .groupby("occupation")["estimate_layoff"].sum().reset_index() \
        .sort_values("estimate_layoff", ascending=False).head(job_top_n)
    top_jobs['occupation'] = top_jobs['occupation'].str.title()

    if not top_jobs.empty:
        fig_jobs = px.bar(top_jobs, x="occupation", y="estimate_layoff",
                         title=f"Top {job_top_n} Occupations by Estimated Layoffs in {selected_state}",
                         color="estimate_layoff",
                         color_continuous_scale=px.colors.sequential.Blues)
        fig_jobs.update_layout(xaxis_title="Occupation", yaxis_title="Layoffs", title_font=dict(size=16))
        st.plotly_chart(fig_jobs, use_container_width=True)
    else:
        st.warning("No occupation data available for selected state.")

    st.markdown("</div>", unsafe_allow_html=True)
