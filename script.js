// Main functionality for FLIC-DUE application
document.addEventListener("DOMContentLoaded", function () {
  // Change View functionality for Home page
  const changeViewBtn = document.getElementById("changeViewBtn");
  const tableView = document.getElementById("tableView");
  const gridView = document.getElementById("gridView");

  if (changeViewBtn) {
    changeViewBtn.addEventListener("click", function () {
      if (tableView.style.display === "none") {
        tableView.style.display = "block";
        gridView.style.display = "none";
        changeViewBtn.classList.remove("active");
      } else {
        tableView.style.display = "none";
        gridView.style.display = "block";
        changeViewBtn.classList.add("active");
      }
    });
  }

  // Profile page tab functionality
  const accountSettingsTab = document.getElementById("accountSettingsTab");
  const recentActivityTab = document.getElementById("recentActivityTab");

  const accountSettingsContent = document.getElementById(
    "accountSettingsContent"
  );
  const recentActivityContent = document.getElementById(
    "recentActivityContent"
  );
  accountSettingsContent.style.display = "block";

  if (accountSettingsTab && recentActivityTab) {
    // Set default active tab
    accountSettingsTab.classList.add("active");

    accountSettingsTab.addEventListener("click", function () {
      // Update tab buttons
      accountSettingsTab.classList.add("active");
      recentActivityTab.classList.remove("active");

      // Update content visibility
      accountSettingsContent.style.display = "block";
      recentActivityContent.style.display = "none";
    });

    recentActivityTab.addEventListener("click", function () {
      // Update tab buttons
      accountSettingsTab.classList.remove("active");
      recentActivityTab.classList.add("active");

      // Update content visibility
      accountSettingsContent.style.display = "none";
      recentActivityContent.style.display = "block";
    });
  }

  // Article Detail Modal
  const articleRows = document.querySelectorAll(".article-row");
  const articleCards = document.querySelectorAll(".article-card");
  const articleDetailModal = document.getElementById("articleDetailModal");

  if (articleRows) {
    articleRows.forEach((row) => {
      row.addEventListener("click", function () {
        if (articleDetailModal) {
          articleDetailModal.classList.add("show");
        }
      });
    });
  }

  if (articleCards) {
    articleCards.forEach((card) => {
      card.addEventListener("click", function () {
        if (articleDetailModal) {
          articleDetailModal.classList.add("show");
        }
      });
    });
  }

  // Close Article Detail Modal
  const backButton = document.querySelector(".back-button");
  if (backButton && articleDetailModal) {
    backButton.addEventListener("click", function () {
      articleDetailModal.classList.remove("show");
    });
  }

  // Search Modal
  const searchInput = document.getElementById("searchInput");
  const searchBtn = document.getElementById("searchBtn");
  const searchModal = document.getElementById("searchModal");

  if (searchInput && searchModal) {
    searchInput.addEventListener("click", function () {
      searchModal.classList.add("show");
    });
  }

  if (searchBtn && searchModal) {
    searchBtn.addEventListener("click", function () {
      searchModal.classList.add("show");
    });
  }

  // Close Search Modal
  const closeSearchBtn = searchModal
    ? searchModal.querySelector(".close-btn")
    : null;
  if (closeSearchBtn && searchModal) {
    closeSearchBtn.addEventListener("click", function () {
      searchModal.classList.remove("show");
    });
  }

  // Account Management
  const viewAccountBtns = document.querySelectorAll(".view-account-btn");
  const deleteAccountBtns = document.querySelectorAll(".delete-account-btn");
  const newAccountBtn = document.getElementById("newAccountBtn");
  const accountModal = document.getElementById("accountModal");
  const deleteAccountModal = document.getElementById("deleteAccountModal");

  if (viewAccountBtns && accountModal) {
    viewAccountBtns.forEach((btn) => {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        accountModal.classList.add("show");
      });
    });
  }

  if (newAccountBtn && accountModal) {
    newAccountBtn.addEventListener("click", function () {
      accountModal.classList.add("show");
    });
  }

  if (deleteAccountBtns && deleteAccountModal) {
    deleteAccountBtns.forEach((btn) => {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        deleteAccountModal.classList.add("show");
      });
    });
  }

  // Close Account Modals
  const closeAccountBtn = accountModal
    ? accountModal.querySelector(".close-btn")
    : null;
  if (closeAccountBtn && accountModal) {
    closeAccountBtn.addEventListener("click", function () {
      accountModal.classList.remove("show");
    });
  }

  const closeDeleteBtn = deleteAccountModal
    ? deleteAccountModal.querySelector(".close-btn")
    : null;
  if (closeDeleteBtn && deleteAccountModal) {
    closeDeleteBtn.addEventListener("click", function () {
      deleteAccountModal.classList.remove("show");
    });
  }

  const noDeleteBtn = deleteAccountModal
    ? deleteAccountModal.querySelector(".btn-secondary")
    : null;
  if (noDeleteBtn && deleteAccountModal) {
    noDeleteBtn.addEventListener("click", function () {
      deleteAccountModal.classList.remove("show");
    });
  }

  // Close modals when clicking outside
  window.addEventListener("click", function (e) {
    if (articleDetailModal && e.target === articleDetailModal) {
      articleDetailModal.classList.remove("show");
    }
    if (searchModal && e.target === searchModal) {
      searchModal.classList.remove("show");
    }
    if (accountModal && e.target === accountModal) {
      accountModal.classList.remove("show");
    }
    if (deleteAccountModal && e.target === deleteAccountModal) {
      deleteAccountModal.classList.remove("show");
    }
  });
});
// Add this to your existing script.js file

document.addEventListener("DOMContentLoaded", function () {
  // Make all article rows and cards clickable to show the article detail modal
  const articleRows = document.querySelectorAll(".article-row");
  const articleCards = document.querySelectorAll(".article-card");
  const articleDetailModal = document.getElementById("articleDetailModal");

  // For table view
  if (articleRows) {
    articleRows.forEach((row) => {
      row.addEventListener("click", function () {
        if (articleDetailModal) {
          articleDetailModal.classList.add("show");
        }
      });
    });
  }

  // For grid view
  if (articleCards) {
    articleCards.forEach((card) => {
      card.addEventListener("click", function () {
        if (articleDetailModal) {
          articleDetailModal.classList.add("show");
        }
      });
    });
  }

  // Public home page article links
  const publicArticleCards = document.querySelectorAll(
    ".article-card, .featured-article"
  );

  if (publicArticleCards) {
    publicArticleCards.forEach((card) => {
      card.addEventListener("click", function () {
        window.location.href = "public-article-detail.html";
      });
    });
  }

  // Back button functionality
  const backButtons = document.querySelectorAll(".back-button, .back-link a");

  if (backButtons) {
    backButtons.forEach((button) => {
      button.addEventListener("click", function (e) {
        // For modal back buttons
        if (articleDetailModal && this.closest(".modal")) {
          e.preventDefault();
          articleDetailModal.classList.remove("show");
        }
        // For page back buttons, let the default behavior work (navigate back)
      });
    });
  }
});
