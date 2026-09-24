"""
translations.py
Bản dịch giao diện cho 3 ngôn ngữ: English (en), Tiếng Việt (vi), Français (fr).

Cách hoạt động (giống hệt cơ chế đổi tiền tệ):
  - Ngôn ngữ được lưu trong session["language"] và cột Users.language.
  - Template gọi {{ t('key') }}; app.py bơm hàm t() qua context_processor.
  - Không dùng gettext / file .po nên KHÔNG cần bước biên dịch nào.

Thêm chuỗi mới: thêm 1 dòng vào _STRINGS với đủ 3 khoá "en"/"vi"/"fr".
Thiếu bản dịch -> tự động rơi về "en" -> rồi về chính cái key.
"""

LANGUAGES = ["en", "vi", "fr"]

# Tên hiển thị trên nút chọn ngôn ngữ trong dropdown avatar
LANGUAGE_NAMES = {"en": "English", "vi": "Tiếng Việt", "fr": "Français"}


_STRINGS = {
    # ---------- Thanh điều hướng / dropdown avatar ----------
    "role_owner":            {"en": "Owner",   "vi": "Chủ",        "fr": "Propriétaire"},
    "role_staff":            {"en": "Staff",   "vi": "Nhân viên",  "fr": "Personnel"},
    "nav_change_avatar":     {"en": "Change avatar",         "vi": "Đổi ảnh đại diện",        "fr": "Changer d'avatar"},
    "nav_currency":          {"en": "Currency",              "vi": "Tiền tệ",                 "fr": "Devise"},
    "nav_language":          {"en": "Language",              "vi": "Ngôn ngữ",               "fr": "Langue"},
    "nav_theme":             {"en": "Light / dark mode",     "vi": "Chế độ sáng / tối",       "fr": "Mode clair / sombre"},
    "nav_manage_staff":      {"en": "Manage staff",          "vi": "Quản lý nhân viên",       "fr": "Gérer le personnel"},
    "nav_manage_menu":       {"en": "Manage menu & tables",  "vi": "Quản lý món & bàn",       "fr": "Gérer le menu et les tables"},
    "nav_sales_report":      {"en": "Sales report",          "vi": "Báo cáo doanh thu",       "fr": "Rapport des ventes"},
    "nav_logout":            {"en": "Log out",               "vi": "Đăng xuất",               "fr": "Déconnexion"},

    # ---------- Đăng nhập ----------
    "login_subtitle":        {"en": "Sign in to continue",   "vi": "Đăng nhập để tiếp tục",   "fr": "Connectez-vous pour continuer"},
    "login_username":        {"en": "Username",              "vi": "Tên đăng nhập",           "fr": "Nom d'utilisateur"},
    "login_password":        {"en": "Password",              "vi": "Mật khẩu",                "fr": "Mot de passe"},
    "login_submit":          {"en": "Sign in",               "vi": "Đăng nhập",               "fr": "Se connecter"},

    # ---------- Sơ đồ bàn ----------
    "tm_takeaway":           {"en": "Takeaway",              "vi": "Mang về",                 "fr": "À emporter"},
    "tm_takeaway_sub":       {"en": "Start a takeaway order, no table needed",
                              "vi": "Tạo đơn mang về, không cần bàn",
                              "fr": "Créer une commande à emporter, sans table"},
    "tm_new_takeaway":       {"en": "+ New Takeaway Order",  "vi": "+ Đơn mang về mới",       "fr": "+ Nouvelle commande à emporter"},
    "tm_title":              {"en": "Table Map",             "vi": "Sơ đồ bàn",               "fr": "Plan des tables"},
    "tm_subtitle":           {"en": "Select a table to start an order",
                              "vi": "Chọn một bàn để bắt đầu gọi món",
                              "fr": "Sélectionnez une table pour commencer une commande"},
    "tm_available":          {"en": "Available",             "vi": "Trống",                   "fr": "Libre"},
    "tm_occupied":           {"en": "Occupied",              "vi": "Đang dùng",               "fr": "Occupée"},
    "tm_seats":              {"en": "seats",                 "vi": "chỗ",                     "fr": "places"},
    "tm_no_tables":          {"en": "No tables found yet.",  "vi": "Chưa có bàn nào.",        "fr": "Aucune table pour l'instant."},

    # ---------- Màn gọi món ----------
    "ord_back":              {"en": "Table Map",             "vi": "Sơ đồ bàn",               "fr": "Plan des tables"},
    "ord_takeaway_title":    {"en": "Takeaway Order",        "vi": "Đơn mang về",             "fr": "Commande à emporter"},
    "ord_table":             {"en": "Table",                 "vi": "Bàn",                     "fr": "Table"},
    "ord_menu":              {"en": "Menu",                  "vi": "Thực đơn",                "fr": "Menu"},
    "ord_show_all":          {"en": "Show All",              "vi": "Tất cả",                  "fr": "Tout afficher"},
    "ord_ticket":            {"en": "Order ticket",          "vi": "Phiếu gọi món",           "fr": "Ticket de commande"},
    "ord_total":             {"en": "Total",                 "vi": "Tổng cộng",               "fr": "Total"},
    "ord_pay":               {"en": "Pay",                   "vi": "Thanh toán",              "fr": "Payer"},
    "ord_add_failed":        {"en": "Couldn't add the item. Please try again.",
                              "vi": "Không thêm được món. Vui lòng thử lại.",
                              "fr": "Impossible d'ajouter l'article. Veuillez réessayer."},
    "ord_pay_failed":        {"en": "Unable to complete payment.",
                              "vi": "Không hoàn tất được thanh toán.",
                              "fr": "Impossible de finaliser le paiement."},
    "ord_pay_success":       {"en": "Payment successful:",   "vi": "Thanh toán thành công:",  "fr": "Paiement réussi :"},

    # ---------- Báo cáo ----------
    "rep_title":             {"en": "Sales Report",          "vi": "Báo cáo doanh thu",       "fr": "Rapport des ventes"},
    "rep_total_revenue":     {"en": "Total revenue",         "vi": "Tổng doanh thu",          "fr": "Chiffre d'affaires total"},
    "rep_period_day":        {"en": "Day",                   "vi": "Ngày",                    "fr": "Jour"},
    "rep_period_week":       {"en": "Week",                  "vi": "Tuần",                    "fr": "Semaine"},
    "rep_period_month":      {"en": "Month",                 "vi": "Tháng",                   "fr": "Mois"},
    "rep_apply":             {"en": "Apply",                 "vi": "Áp dụng",                 "fr": "Appliquer"},
    "rep_dine_in":           {"en": "Dine-in",               "vi": "Ăn tại chỗ",              "fr": "Sur place"},
    "rep_takeaway":          {"en": "Takeaway",              "vi": "Mang về",                 "fr": "À emporter"},
    "rep_bills":             {"en": "bills",                 "vi": "hoá đơn",                 "fr": "factures"},
    "rep_no_dine_in":        {"en": "No dine-in sales in this period.",
                              "vi": "Không có doanh thu ăn tại chỗ trong kỳ này.",
                              "fr": "Aucune vente sur place sur cette période."},
    "rep_no_takeaway":       {"en": "No takeaway sales in this period.",
                              "vi": "Không có doanh thu mang về trong kỳ này.",
                              "fr": "Aucune vente à emporter sur cette période."},

    # ---------- Quản lý nhân viên ----------
    "stf_title":             {"en": "Staff Accounts",        "vi": "Tài khoản nhân viên",     "fr": "Comptes du personnel"},
    "stf_subtitle":          {"en": "Owner-only. Create accounts for your staff to use.",
                              "vi": "Chỉ dành cho chủ. Tạo tài khoản cho nhân viên sử dụng.",
                              "fr": "Réservé au propriétaire. Créez des comptes pour votre personnel."},
    "stf_add_new":           {"en": "Add new staff",         "vi": "Thêm nhân viên mới",      "fr": "Ajouter un employé"},
    "stf_add_button":        {"en": "Add staff",             "vi": "Thêm nhân viên",          "fr": "Ajouter"},
    "stf_existing":          {"en": "Existing staff",        "vi": "Nhân viên hiện có",       "fr": "Personnel existant"},
    "stf_new_password_ph":   {"en": "New password (optional)",
                              "vi": "Mật khẩu mới (không bắt buộc)",
                              "fr": "Nouveau mot de passe (facultatif)"},
    "stf_none":              {"en": "No staff accounts yet.","vi": "Chưa có tài khoản nhân viên.","fr": "Aucun compte pour l'instant."},

    # ---------- Quản lý món & bàn ----------
    "mm_title":              {"en": "Manage Menu & Tables",  "vi": "Quản lý món & bàn",       "fr": "Gérer le menu et les tables"},
    "mm_subtitle":           {"en": "Owner-only. Add, edit, or remove dishes and tables. Prices are entered and stored in VND; the currency selector in the top bar only changes how they're displayed elsewhere.",
                              "vi": "Chỉ dành cho chủ. Thêm, sửa hoặc xoá món và bàn. Giá nhập và lưu theo VND; nút chọn tiền tệ trên thanh trên cùng chỉ đổi cách hiển thị ở nơi khác.",
                              "fr": "Réservé au propriétaire. Ajoutez, modifiez ou supprimez des plats et des tables. Les prix sont saisis et stockés en VND ; le sélecteur de devise en haut ne change que l'affichage ailleurs."},
    "mm_add_dish":           {"en": "Add a new dish",        "vi": "Thêm món mới",            "fr": "Ajouter un plat"},
    "mm_dish_name_ph":       {"en": "Dish name",             "vi": "Tên món",                 "fr": "Nom du plat"},
    "mm_category_ph":        {"en": "Category", "vi": "Nhóm món", "fr": "Catégorie"},
    "mm_price_ph":           {"en": "Price (VND)",           "vi": "Giá (VND)",               "fr": "Prix (VND)"},
    "mm_vegetarian":         {"en": "Vegetarian",            "vi": "Món chay",                "fr": "Végétarien"},
    "mm_add_dish_button":    {"en": "Add dish",              "vi": "Thêm món",                "fr": "Ajouter le plat"},
    "mm_current_dishes":     {"en": "Current dishes",        "vi": "Danh sách món",           "fr": "Plats actuels"},
    "mm_veg_short":          {"en": "Veg",                   "vi": "Chay",                    "fr": "Végé"},
    "mm_save":               {"en": "Save",                  "vi": "Lưu",                     "fr": "Enregistrer"},
    "mm_remove":             {"en": "Delete",                "vi": "Xoá",                     "fr": "Supprimer"},
    "mm_removed":            {"en": "Deleted",               "vi": "Đã xoá",                  "fr": "Supprimé"},
    "mm_restore":            {"en": "Restore",               "vi": "Khôi phục",               "fr": "Restaurer"},
    "mm_add_table":          {"en": "Add a new table",       "vi": "Thêm bàn mới",            "fr": "Ajouter une table"},
    "mm_seats_ph":           {"en": "Number of seats",       "vi": "Số chỗ ngồi",             "fr": "Nombre de places"},
    "mm_add_table_button":   {"en": "Add table",             "vi": "Thêm bàn",                "fr": "Ajouter la table"},
    "mm_current_tables":     {"en": "Current tables",        "vi": "Danh sách bàn",           "fr": "Tables actuelles"},
    "mm_table":              {"en": "Table",                 "vi": "Bàn",                     "fr": "Table"},
    "mm_delete":             {"en": "Delete",                "vi": "Xoá",                     "fr": "Supprimer"},

    # Trạng thái bàn lưu trong DB (available / in_use) -> nhãn hiển thị
    "status_available":      {"en": "Available",             "vi": "Trống",                   "fr": "Libre"},
    "status_in_use":         {"en": "In use",                "vi": "Đang dùng",               "fr": "Occupée"},

    # ---------- Thông báo lỗi sinh ở backend ----------
    "err_bad_login":         {"en": "Invalid username or password.",
                              "vi": "Sai tên đăng nhập hoặc mật khẩu.",
                              "fr": "Nom d'utilisateur ou mot de passe invalide."},
    "err_username_empty":    {"en": "Username cannot be empty.",
                              "vi": "Tên đăng nhập không được để trống.",
                              "fr": "Le nom d'utilisateur ne peut pas être vide."},
    "err_fill_user_pass":    {"en": "Please fill in both username and password.",
                              "vi": "Vui lòng nhập cả tên đăng nhập và mật khẩu.",
                              "fr": "Veuillez renseigner le nom d'utilisateur et le mot de passe."},
    "err_fill_dish":         {"en": "Please fill in the dish name and price.",
                              "vi": "Vui lòng nhập tên món và giá.",
                              "fr": "Veuillez renseigner le nom du plat et le prix."},
    "err_fill_seats":        {"en": "Please enter the number of seats.",
                              "vi": "Vui lòng nhập số chỗ ngồi.",
                              "fr": "Veuillez indiquer le nombre de places."},
    "err_price_invalid":     {"en": "Enter a valid price (0 or more).",
                              "vi": "Nhập giá hợp lệ (từ 0 trở lên).",
                              "fr": "Saisissez un prix valide (0 ou plus)."},
    "err_seats_invalid":     {"en": "Seats must be a whole number of at least 1.",
                              "vi": "Số chỗ phải là số nguyên từ 1 trở lên.",
                              "fr": "Le nombre de places doit être un entier d'au moins 1."},
    "err_username_taken":    {"en": "This username is already taken.",
                              "vi": "Tên đăng nhập này đã có người dùng.",
                              "fr": "Ce nom d'utilisateur est déjà pris."},
    "err_table_has_history": {"en": "Cannot delete a table that already has order/bill history.",
                              "vi": "Không thể xoá bàn đã có lịch sử gọi món / hoá đơn.",
                              "fr": "Impossible de supprimer une table ayant déjà un historique de commandes/factures."},
    "err_bill_empty":        {"en": "This bill has no items yet",
                              "vi": "Hoá đơn này chưa có món nào",
                              "fr": "Cette facture ne contient encore aucun article"},
    "err_invalid_color":     {"en": "Invalid color",         "vi": "Màu không hợp lệ",        "fr": "Couleur invalide"},
    "err_invalid_currency":  {"en": "Invalid currency",      "vi": "Tiền tệ không hợp lệ",    "fr": "Devise invalide"},
    "err_invalid_language":  {"en": "Invalid language",      "vi": "Ngôn ngữ không hợp lệ",   "fr": "Langue invalide"},
}


# Tên thứ trong tuần (0 = Thứ Hai, khớp với date.weekday())
WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "vi": ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"],
    "fr": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
}

# Tên tháng (index 0 = tháng 1)
MONTHS = {
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "vi": ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
           "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
}


def _normalize(lang):
    return lang if lang in LANGUAGES else "en"


def t(key, lang="en"):
    """Dịch 1 key. Không có key -> trả về chính key (để dễ phát hiện chuỗi thiếu)."""
    lang = _normalize(lang)
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(lang) or entry.get("en") or key


def weekday_name(weekday_index, lang="en"):
    return WEEKDAYS[_normalize(lang)][weekday_index]


def month_name(month_number, lang="en"):
    """month_number: 1-12."""
    return MONTHS[_normalize(lang)][month_number - 1]
