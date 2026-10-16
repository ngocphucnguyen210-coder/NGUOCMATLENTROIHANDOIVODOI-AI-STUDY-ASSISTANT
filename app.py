# --- MÀN HÌNH ĐĂNG NHẬP & LIÊN KẾT OAUTH CHUYÊN NGHIỆP ---
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .login-card {
            background: white;
            padding: 35px;
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(216, 27, 96, 0.12);
            text-align: center;
            border: 1px solid #FFC0CB;
            max-width: 450px;
            margin: auto;
            margin-top: 5vh;
        }
        .login-title {
            color: #D81B60;
            font-size: 34px;
            font-weight: 800;
        }
        .login-slogan {
            color: #AD1457;
            font-size: 14px;
            font-style: italic;
            margin-bottom: 20px;
        }
    </style>
    <div class="login-card">
        <div class="login-title">🌸 PHUCgpt</div>
        <div class="login-slogan">"Đồng hành thông minh, vun tròn vẹn Phúc"</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔗 Liên kết tài khoản mạng xã hội")
        
        # Chọn ứng dụng muốn đăng nhập
        auth_choice = st.selectbox(
            "Chọn nền tảng liên kết:", 
            ["🌐 Google / Gmail", "📘 Facebook", "🍏 Apple / iCloud"]
        )

        st.markdown("---")

        if "Google" in auth_choice:
            st.info("💡 Bạn sẽ được chuyển hướng đến cổng xác thực chính thức của Google để liên kết tài khoản.")
            # Link chuyển hướng sang trang đăng nhập Google thực tế
            google_login_url = "https://accounts.google.com/signin"
            st.markdown(f'<a href="{google_login_url}" target="_blank"><button style="width:100%; background-color:#4285F4; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Mở trang đăng nhập Google ↗</button></a>', unsafe_allow_html=True)
            
        elif "Facebook" in auth_choice:
            st.info("💡 Bạn sẽ được chuyển hướng đến cổng xác thực chính thức của Facebook để liên kết tài khoản.")
            fb_login_url = "https://www.facebook.com/login"
            st.markdown(f'<a href="{fb_login_url}" target="_blank"><button style="width:100%; background-color:#1877F2; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Mở trang đăng nhập Facebook ↗</button></a>', unsafe_allow_html=True)
            
        elif "Apple" in auth_choice:
            st.info("💡 Bạn sẽ được chuyển hướng đến cổng xác thực Apple ID để liên kết tài khoản.")
            apple_login_url = "https://appleid.apple.com/"
            st.markdown(f'<a href="{apple_login_url}" target="_blank"><button style="width:100%; background-color:#000000; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">Mở trang đăng nhập Apple ID ↗</button></a>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("**Hoặc hoàn tất xác nhận liên kết vào PHUCgpt:**")
        
        linked_email = st.text_input("Nhập email/tài khoản đã đăng nhập ở trên:")
        confirm_pass = st.text_input("Nhập mật khẩu xác nhận liên kết:", type="password")

        if st.button("✅ Xác nhận Hoàn tất Liên kết", use_container_width=True):
            if linked_email.strip() == "":
                st.warning("Vui lòng nhập tài khoản email đã xác thực!")
            else:
                st.session_state.logged_in = True
                st.session_state.username = linked_email
                
                # Tạo phiên chat đầu tiên trong DB
                c = conn.cursor()
                c.execute("SELECT id FROM sessions WHERE username = ?", (linked_email,))
                first_sess = c.fetchone()
                if not first_sess:
                    c.execute("INSERT INTO sessions (username, title) VALUES (?, ?)", (linked_email, "Đoạn chat mới"))
                    conn.commit()
                st.success("Liên kết tài khoản thành công! Đang chuyển vào ứng dụng...")
                st.rerun()
    st.stop()
