const homeLayout = document.querySelector("[data-home-layout]");

if (homeLayout) {
  const mainColumn = homeLayout.querySelector("[data-home-main]");
  const fbEmbed = homeLayout.querySelector("[data-fb-embed]");

  const syncEmbedHeight = () => {
    if (!mainColumn || !fbEmbed) {
      return;
    }

    if (window.innerWidth <= 980) {
      fbEmbed.style.removeProperty("--fb-embed-height");
      return;
    }

    const mainHeight = Math.ceil(mainColumn.getBoundingClientRect().height);
    if (mainHeight > 0) {
      fbEmbed.style.setProperty("--fb-embed-height", `${mainHeight}px`);
    }
  };

  window.addEventListener("load", syncEmbedHeight);
  window.addEventListener("resize", syncEmbedHeight);
  syncEmbedHeight();
}
