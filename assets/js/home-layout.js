const homeLayout = document.querySelector("[data-home-layout]");

if (homeLayout) {
  const mainColumn = homeLayout.querySelector("[data-home-main]");
  const fbEmbed = homeLayout.querySelector("[data-fb-embed]");
  const fbFrame = fbEmbed?.querySelector("iframe");

  const syncEmbedHeight = () => {
    if (!mainColumn || !fbEmbed || !fbFrame) {
      return;
    }

    if (window.innerWidth <= 980) {
      fbEmbed.style.removeProperty("--fb-embed-height");
      fbFrame.style.removeProperty("height");
      fbFrame.removeAttribute("height");
      return;
    }

    const mainHeight = Math.ceil(mainColumn.getBoundingClientRect().height);
    if (mainHeight > 0) {
      const targetHeight = `${mainHeight}px`;
      fbEmbed.style.setProperty("--fb-embed-height", targetHeight);
      fbFrame.style.height = targetHeight;
      fbFrame.setAttribute("height", String(mainHeight));
    }
  };

  window.addEventListener("load", syncEmbedHeight);
  window.addEventListener("resize", syncEmbedHeight);
  syncEmbedHeight();
}
