// topbar.js
// Mở/đóng dropdown khi bấm avatar, và gọi API đổi màu avatar khi chọn swatch.

document.addEventListener("DOMContentLoaded", () => {
  const avatarButton = document.getElementById("avatar-button");
  const dropdown = document.getElementById("avatar-dropdown");

  avatarButton.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdown.classList.toggle("avatar-dropdown--open");
  });

  document.addEventListener("click", () => {
    dropdown.classList.remove("avatar-dropdown--open");
  });

  document.querySelectorAll(".avatar-swatch").forEach((swatch) => {
    swatch.addEventListener("click", async (e) => {
      e.stopPropagation();
      const color = swatch.dataset.color;

      const res = await fetch("/api/profile/avatar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ color }),
      });

      if (res.ok) {
        avatarButton.style.background = color;
      }
    });
  });

  // Đổi tiền tệ hiển thị -> load lại trang để mọi số tiền hiện đúng đơn vị mới
  document.querySelectorAll(".currency-option").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const currency = btn.dataset.currency;

      const res = await fetch("/api/profile/currency", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ currency }),
      });

      if (res.ok) {
        window.location.reload();
      }
    });
  });

  // Đổi ngôn ngữ (nút EN / VI / FR bên trái avatar) -> load lại trang
  document.querySelectorAll(".lang-switch__option").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const language = btn.dataset.language;

      const res = await fetch("/api/profile/language", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language }),
      });

      if (res.ok) {
        window.location.reload();
      }
    });
  });

  // Nút mặt trăng / mặt trời: bật tắt nền tối, nhớ lựa chọn trong localStorage.
  // Không load lại trang - chỉ đổi thuộc tính data-theme trên <html>.
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const root = document.documentElement;
      const goingDark = root.getAttribute("data-theme") !== "dark";
      if (goingDark) {
        root.setAttribute("data-theme", "dark");
      } else {
        root.removeAttribute("data-theme");
      }
      try {
        localStorage.setItem("theme", goingDark ? "dark" : "light");
      } catch (err) {}
    });
  }

  // Ô nhập số (giá món, số chỗ ngồi):
  //  - lăn chuột không được tự đổi giá trị -> chỉ cần blur khi cuộn
  //  - chặn gõ dấu "-" và "e" nên không nhập được số âm / ký hiệu mũ
  document.querySelectorAll('input[type="number"]').forEach((el) => {
    el.addEventListener("wheel", () => el.blur(), { passive: true });
    el.addEventListener("keydown", (e) => {
      if (e.key === "-" || e.key === "+" || e.key === "e" || e.key === "E") {
        e.preventDefault();
      }
    });
  });
});
