// declare global variables
var emails_view, email_view, compose_view;

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

  // Initialize global variables
  emails_view = document.querySelector('#emails-view');
  compose_view = document.querySelector('#compose-view');

  // Add email view section
  email_view = document.createElement('div');
  email_view.id = '#email-view';
  document.querySelector('.container').insertBefore(email_view, compose_view);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(prev_email=null) {
  
  // Handle error if any
  let err_msg = null;

  function handleSendEmailError(error) {
    if (err_msg === null) {
      err_msg = document.createElement('p');
      err_msg.style.color = 'red';
      err_msg.style.fontWeight= 'bold';
      compose_view.insertBefore(err_msg, document.querySelector('form'));
    }
    err_msg.innerHTML = error;
    window.scrollTo(0, 0);
  }

  // Show compose view and hide other views
  emails_view.style.display = 'none';
  email_view.style.display = 'none';
  compose_view.style.display = 'block';

  // Clear out composition fields
  const recipients = document.querySelector('#compose-recipients');
  const subject = document.querySelector('#compose-subject');
  const body = document.querySelector('#compose-body');
  
  if (prev_email) {
    recipients.value = prev_email.sender;
    subject.value = (prev_email.subject !== '') ? ((/^Re:.*/.test(prev_email.subject)) ? prev_email.subject : 'Re: ' + prev_email.subject) : '';
    body.value = `On ${prev_email.timestamp} ${prev_email.sender} wrote:\n${prev_email.body}`;
  } else {
    recipients.value = '';
    subject.value = '';
    body.value = '';
  }

  // Send email on submit button click
  document.querySelector('form').onsubmit = () => {

    // Validate user input
    if (subject.value === '' || /^\s+$/.test(subject.value)) {
      handleSendEmailError('Please add some email subject.');
      return false;
    } else if (body.value === '' || /^\s+$/.test(body.value)) {
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
  emails_view.style.display = 'block';
  email_view.style.display = 'none';
  compose_view.style.display = 'none';

  // Show the mailbox name
  emails_view.innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

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
    } else if (emails.length === 0) {
      err_msg = document.createElement('p');
      err_msg.innerHTML = 'You do not have emails in this mailbox.'
      emails_view.append(err_msg);
    } else {
      let sent = (mailbox === 'sent') ? true : false;
      emails_view.append(get_header(sent));
      emails.forEach(email => {
        emails_view.classList += 'container';
        emails_view.append(get_msg(email, sent));
      })
    }
  })

}

function get_header(sent) {
  // create header for mailbox views
  const header = document.createElement('div');
  header.classList += 'row';

  const hfrom = document.createElement('div');
  hfrom.classList += 'col-4';
  hfrom.innerHTML = (sent) ? 'To' : 'From';

  const hsubject = document.createElement('div');
  hsubject.classList += 'col-5';
  hsubject.innerHTML = 'Subject';

  const hdt = document.createElement('div');
  hdt.classList += 'col-3';
  hdt.innerHTML = 'Time';

  header.append(...[hfrom, hsubject, hdt]);

  return header;
}

function get_msg(email, sent) {
  // message container
  let msg = document.createElement('div');
  msg.classList += 'row mb-1 border border-top-1 border-bottom-1 border-left-1 border-right-1';
  if (email.read) {
    msg.classList += 'bg bg-light';
   }
  msg.onmouseover = () => {msg.style.opacity = '0.7'; msg.style.cursor = 'pointer'};
  msg.onmouseout = () => {msg.style.opacity = '1.0'};
  msg.addEventListener('click', () => load_email(email.id));
  // 'from' column
  let from = document.createElement('div');
  from.classList += 'col-4';
  from.innerHTML = (sent) ? email.recipients.join('; ') : email.sender;
  // 'subject' column
  let subject = document.createElement('div');
  subject.classList += 'col-5';
  subject.innerHTML = email.subject;
  // timestamp column
  let dt = document.createElement('div');
  dt.classList += 'col-3';
  dt.innerHTML = email.timestamp;
  // create row
  msg.append(...[from, subject, dt]);

  return msg;
}

function load_email(id) {

  // Show the email and hide other views
  emails_view.style.display = 'none';
  email_view.style.display = 'block';
  compose_view.style.display = 'none';

  // Add header
  email_view.innerHTML = '<h3>E-mail message</h3>';
  // store email elements
  let elements = [];

  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    // prepare email
    // timestamp
    let timestamp = document.createElement('span');
    timestamp.innerHTML = `Sent on: ${email.timestamp}`;
    elements.push(timestamp);
    // reply button
    let reply_button = document.createElement('span');
    reply_button.classList += 'btn btn-primary m-2';
    reply_button.innerText = "Reply";
    reply_button.addEventListener('click', () => compose_email(email));
    elements.push(reply_button);
    // container
    let email_container = document.createElement('div');
    email_container.className = 'container';
    // email elements template
    let email_object = {};
    // write content to elements
    for (var key in email) {
      if (key === "sender" || key === "recipients" || key === "subject" || key === "body") {
        Object.defineProperty(email_object, key, {
          value: null,
          writable: true,
          enumerable: true,
          configurable: true,
        });
        email_object[key] = document.createElement('div');
        email_object[key].className = 'row';
        if (key !== 'body') {
          email_object[key].innerHTML = `<div class='col-4'>${key.charAt(0).toUpperCase() + key.slice(1)}:</div><div class='col-8'><b>${(key === 'recipients') ? email[key].join('; ') : email[key]}</b></div>`;
        } else {
          console.log(email[key]);
          email_object[key].innerHTML = `<div class='col-12'>Message text:</div><div class='col-12 bg bg-light border' style='height: 100px;'>${email[key].replace(/\r?\n/g, '<br />')}</div>`;
        }
        elements.push(email_object[key]);
      }
    }
    // display email message
    email_view.append(...elements);
    // mark email as read
    fetch(`/emails/${email.id}`, {
      method: 'PUT',
      body: JSON.stringify({
          read: true
      })
    });
  })
  .catch(error => {
    let err_msg = document.createElement('p');
    err_msg.innerHTML = `Error: ${error}`;
    email_view.append(err_msg);
  });
}
