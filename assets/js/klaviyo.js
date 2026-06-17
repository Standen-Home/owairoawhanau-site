(function(){
  const companyId = 'S4tXRU';
  let loadingPromise;

  function loadKlaviyo(){
    if(window.klaviyo || window._klaviyoLoaded){
      return Promise.resolve();
    }

    if(loadingPromise){
      return loadingPromise;
    }

    window._klOnsite = window._klOnsite || [];
    loadingPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://static.klaviyo.com/onsite/js/${companyId}/klaviyo.js?company_id=${companyId}`;
      script.onload = () => {
        window._klaviyoLoaded = true;
        resolve();
      };
      script.onerror = reject;
      document.head.appendChild(script);
    });

    return loadingPromise;
  }

  function openForm(formId){
    window._klOnsite = window._klOnsite || [];
    window._klOnsite.push(['openForm', formId]);
    loadKlaviyo().catch(() => {});
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('[data-klaviyo-form]');
    if(!button){
      return;
    }

    const formId = button.getAttribute('data-klaviyo-form');
    if(formId){
      openForm(formId);
    }
  });
})();
