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
  document.querySelector('#emails-view').style.display = 'none';
  const compose_view = document.querySelector('#compose-view');
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

    // Prevent default submit form behaviour
    return false;
  };
}

function load_mailbox(mailbox) {

  let err_msg;
  
  // Show the mailbox and hide other views
  const emails_view = document.querySelector('#emails-view');
  emails_view.style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Load mailbox
  fetch('/emails/' + mailbox)
  .then(response => response.json())
  .then(emails => {
    if (emails.error) {
      err_msg = document.createElement('p');
      err_msg.style.fontWeight = 'bold';
      err_msg.style.color = 'red';
      err_msg.innerHTML('Error: ' + emails.error);
      emails_view.append(err_msg);
    } else {
      let sent = (mailbox === 'sent') ? true : false;
      emails_view.append(get_header(sent));
      emails.forEach(email => {
        emails_view.append(get_msg(email, sent));
      })
    }
  })

}

function get_header(sent) {
  // create header for mailbox views
  const header = document.createElement('div');
  header.classList += 'row w-100 m-2';

  const hfrom = document.createElement('div');
  hfrom.classList += 'col-4 p-1';
  hfrom.innerHTML = (sent) ? 'To' : 'From';

  const hsubject = document.createElement('div');
  hsubject.classList += 'col-5 p-1';
  hsubject.innerHTML = 'Subject';

  const hdt = document.createElement('div');
  hdt.classList += 'col-3 p-1';
  hdt.innerHTML = 'Time';

  header.append(...[hfrom, hsubject, hdt]);

  return header;
}

function get_msg(email, sent) {
  // message container
  msg = document.createElement('div');
  msg.classList += 'row w-100 border border-top-1 border-bottom-1 border-left-1 border-right-1 m-2';
  (email.read) ? msg.classList += 'bg bg-light' : msg.classList += '';
  msg.onmouseover = () => {msg.style.opacity = '0.7'; msg.style.cursor = 'pointer'};
  msg.onmouseout = () => {msg.style.opacity = '1.0'};
  msg.addEventListener('click', () => load_email(email.id));
  // 'from' column
  from = document.createElement('div');
  from.classList += 'col-4 p-1';
  from.innerHTML = (sent) ? email.recipient : email.sender;
  // 'subject' column
  subject = document.createElement('div');
  subject.classList += 'col-5 p-1';
  subject.innerHTML = email.subject;
  // timestamp column
  dt = document.createElement('div');
  dt.classList += 'col-3 p-1';
  dt.innerHTML = email.timestamp;
  // create row
  msg.append(...[from, subject, dt]);

  return msg;
}

function load_email(id) {
  // TODO
  return false;
}