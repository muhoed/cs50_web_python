document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  
  // Handle error if any
  let err_msg = null;

  function handleSendEmailError(error) {
    if (err_msg === null) {
      err_msg = document.createElement('p');
      err_msg.style.color = 'red';
      err_msg.style.fontWeight= 'bold';
      document.querySelector('#compose-view').insertBefore(err_msg, document.querySelector('form'));
    }
    err_msg.innerHTML = error;
    window.scrollTo(0, 0);
  }

  // Show compose view and hide other views
  const emails_view = document.querySelector('#emails-view');
  const compose_view = document.querySelector('#compose-view');
  emails_view.style.display = 'none';
  compose_view.style.display = 'block';

  // Clear out composition fields
  const recipients = document.querySelector('#compose-recipients');
  const subject = document.querySelector('#compose-subject');
  const body = document.querySelector('#compose-body');
  
  recipients.value = '';
  subject.value = '';
  body.value = '';

  // Send email on submit button click
  document.querySelector('form').onsubmit = () => {

    // Validate user input
    if (subject.value === '' || /\s+/.test(subject.value)) {
      handleSendEmailError('Please add some email subject.');
      return false;
    } else if (body.value === '' || /\s+/.test(body.value)) {
      handleSendEmailError('Please add some email content.');
      return false;
    }

    // Send email
    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: recipients.value,
          subject: subject.value,
          body: body.value
      })
    })
    .then(response => response.json())
    .then(result => {
        if (!result.error) {
          console.log('Email was sent.');
          load_mailbox('sent');
        } else {
          handleSendEmailError(result.error);
        }
    })
    .catch(error => {
      // Print error
      console.log('Fetch data error: ' + error);
    });

    // Prevent default onsubmit form behaviour
    return false;
  };
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}