// order.js
// Clicking a dish calls the add-item API and updates the receipt live, no page reload.
// Money is already formatted server-side (in the correct currency) - no client-side math needed.

document.addEventListener("DOMContentLoaded", () => {
  const receipt = document.querySelector(".receipt");
  const billId = receipt.dataset.billId;

  // Chuỗi thông báo đã được dịch sẵn ở server, gắn vào data-* của .receipt
  const MSG = {
    addFailed: receipt.dataset.i18nAddFailed,
    payFailed: receipt.dataset.i18nPayFailed,
    paySuccess: receipt.dataset.i18nPaySuccess,
  };

  const itemsList = document.getElementById("receipt-items");
  const totalEl = document.getElementById("receipt-total");
  const payButton = document.getElementById("pay-button");

  function renderItems(items) {
    itemsList.innerHTML = "";
    items.forEach((item) => {
      const li = document.createElement("li");
      li.className = "receipt__line";
      li.innerHTML = `
        <span class="receipt__line-name">${item.name_dish} &times;${item.dish_quantity}</span>
        <span class="receipt__line-price">${item.total_dish_formatted}</span>
      `;
      itemsList.appendChild(li);
    });
  }

  // Click a dish card -> call the API to add it to the current bill
  document.querySelectorAll(".dish-card").forEach((card) => {
    card.addEventListener("click", async () => {
      const menuId = card.dataset.menuId;

      const res = await fetch(`/api/bill/${billId}/add_item`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ menu_id: menuId }),
      });

      if (!res.ok) {
        alert(MSG.addFailed);
        return;
      }

      const data = await res.json();
      renderItems(data.items);
      totalEl.textContent = data.total_formatted;
    });
  });

  // Bấm Thanh toán
  payButton.addEventListener("click", async () => {
    const res = await fetch(`/api/bill/${billId}/pay`, { method: "POST" });
    const data = await res.json();

    if (!res.ok) {
      alert(data.error || MSG.payFailed);
      return;
    }

    alert(`${MSG.paySuccess} ${data.total_formatted}`);
    window.location.href = "/";
  });

  // Category tabs - filter which dish cards are visible, no page reload
  const tabs = document.querySelectorAll(".category-tab");
  const dishCards = document.querySelectorAll(".dish-card");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("category-tab--active"));
      tab.classList.add("category-tab--active");

      const selected = tab.dataset.category;
      dishCards.forEach((card) => {
        const show = selected === "all" || card.dataset.category === selected;
        card.style.display = show ? "" : "none";
      });
    });
  });
});
