(function () {
  "use strict";

  let forms = document.querySelectorAll('.php-email-form');

  forms.forEach(function (form) {
    form.addEventListener('submit', function (event) {
      event.preventDefault();

      const action = form.getAttribute('action');
      const recaptcha = form.getAttribute('data-recaptcha-site-key');

      const loading = form.querySelector('.loading');
      const errorMsg = form.querySelector('.error-message');
      const successMsg = form.querySelector('.sent-message');

      if (!action) {
        if (errorMsg) {
          errorMsg.innerHTML = 'Form action URL is missing.';
          errorMsg.classList.add('d-block');
        }
        return;
      }

      if (loading) loading.classList.add('d-block');
      if (errorMsg) errorMsg.classList.remove('d-block');
      if (successMsg) successMsg.classList.remove('d-block');

      let formData = new FormData(form);

      if (recaptcha) {
        if (typeof grecaptcha !== "undefined") {
          grecaptcha.ready(function () {
            try {
              grecaptcha.execute(recaptcha, { action: 'php_email_form_submit' })
                .then(token => {
                  formData.set('recaptcha-response', token);
                  submitForm(form, action, formData, loading, errorMsg, successMsg);
                });
            } catch (error) {
              showError(form, error, loading, errorMsg);
            }
          });
        } else {
          showError(form, 'reCaptcha API not loaded!', loading, errorMsg);
        }
      } else {
        submitForm(form, action, formData, loading, errorMsg, successMsg);
      }
    });
  });

  function submitForm(form, action, formData, loading, errorMsg, successMsg) {
    fetch(action, {
      method: 'POST',
      body: formData,
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(response => {
        if (response.ok) return response.text();
        else throw new Error(`${response.status} ${response.statusText} ${response.url}`);
      })
      .then(data => {
        if (loading) loading.classList.remove('d-block');
        if (data.trim() === 'OK') {
          if (successMsg) successMsg.classList.add('d-block');
          form.reset();
        } else {
          throw new Error(data ? data : 'No success message returned');
        }
      })
      .catch(error => {
        showError(form, error, loading, errorMsg);
      });
  }

  function showError(form, error, loading, errorMsg) {
    if (loading) loading.classList.remove('d-block');
    if (errorMsg) {
      errorMsg.innerHTML = error;
      errorMsg.classList.add('d-block');
    }
  }
})();
