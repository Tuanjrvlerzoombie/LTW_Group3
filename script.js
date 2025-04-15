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
  const myArticlesTab = document.getElementById("myArticlesTab");
  const accountSettingsTab = document.getElementById("accountSettingsTab");
  const recentActivityTab = document.getElementById("recentActivityTab");

  const myArticlesContent = document.getElementById("myArticlesContent");
  const accountSettingsContent = document.getElementById(
    "accountSettingsContent"
  );
  const recentActivityContent = document.getElementById(
    "recentActivityContent"
  );

  if (myArticlesTab && accountSettingsTab && recentActivityTab) {
    // Set default active tab
    myArticlesTab.classList.add("active");

    myArticlesTab.addEventListener("click", function () {
      // Update tab buttons
      myArticlesTab.classList.add("active");
      accountSettingsTab.classList.remove("active");
      recentActivityTab.classList.remove("active");

      // Update content visibility
      myArticlesContent.style.display = "block";
      accountSettingsContent.style.display = "none";
      recentActivityContent.style.display = "none";
    });

    accountSettingsTab.addEventListener("click", function () {
      // Update tab buttons
      myArticlesTab.classList.remove("active");
      accountSettingsTab.classList.add("active");
      recentActivityTab.classList.remove("active");

      // Update content visibility
      myArticlesContent.style.display = "none";
      accountSettingsContent.style.display = "block";
      recentActivityContent.style.display = "none";
    });

    recentActivityTab.addEventListener("click", function () {
      // Update tab buttons
      myArticlesTab.classList.remove("active");
      accountSettingsTab.classList.remove("active");
      recentActivityTab.classList.add("active");

      // Update content visibility
      myArticlesContent.style.display = "none";
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

  // New Template Modal
  const newTemplateBtn = document.getElementById("newTemplateBtn");
  const newTemplateModal = document.getElementById("newTemplateModal");

  if (newTemplateBtn && newTemplateModal) {
    newTemplateBtn.addEventListener("click", function () {
      newTemplateModal.classList.add("show");
    });
  }

  // Close New Template Modal
  const cancelTemplateBtn = newTemplateModal
    ? newTemplateModal.querySelector(".cancel-btn")
    : null;
  if (cancelTemplateBtn && newTemplateModal) {
    cancelTemplateBtn.addEventListener("click", function () {
      newTemplateModal.classList.remove("show");
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
    if (newTemplateModal && e.target === newTemplateModal) {
      newTemplateModal.classList.remove("show");
    }
    if (accountModal && e.target === accountModal) {
      accountModal.classList.remove("show");
    }
    if (deleteAccountModal && e.target === deleteAccountModal) {
      deleteAccountModal.classList.remove("show");
    }
  });
});
