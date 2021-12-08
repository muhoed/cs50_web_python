import psutil

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC

from auctions.models import *


class TestSeleniumCreateProfileView(StaticLiveServerTestCase):
    """
    Tests JS functionality of create profile view using Selenium Python
    binding and Firefox webdriver.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        #workaround to avoid 'connection refused' error if there is non-finished webdriver instance
        for c in range(5):
            try:
                binary = FirefoxBinary('/usr/lib/firefox/firefox')
                cls.selenium = webdriver.Firefox(firefox_binary=binary)
                cls.selenium.implicitly_wait(10)
                break
            except WebDriverException:
                PROCNAME = "geckodriver"
                for proc in psutil.process_iter():
                    if proc.name() == PROCNAME:
                        proc.kill()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()    
    
    def setUp(self):
        """
        Prepare data common for all tests in this class.
        """
        User.objects.create_user("test_user1", "", 'Pass1')
        self.user = User.objects.get(username='test_user1')
        if self.user is not None:
            self.client.force_login(self.user)
        self.cookie = self.client.cookies['sessionid']
        
        #selenium initialization
        self.selenium.get(self.live_server_url + '/')
        self.selenium.add_cookie({'name': 'sessionid', 'value': self.cookie.value, 'secure': False, 'path': '/'})
        self.selenium.refresh()
        #open create profile page in browser
        self.selenium.get("%s%s%d" % (
                                    self.live_server_url, 
                                    "/create_profile/", 
                                    self.user.pk
                                    ))

    def test_create_profile_add_remove_email_forms(self):
        """
        Test that JS functions to add and remove email address forms
        work as intended.
        """
        #check if email forms are not displayed and marked as 'deleted' 
        #by default
        email_form_1 = self.selenium.find_element_by_id("email-address-form-0")
        email_form_2 = self.selenium.find_element_by_id("email-address-form-1")
        self.assertFalse(email_form_1.is_displayed())
        self.assertFalse(email_form_2.is_displayed())
        #add first email form                        
        add_email_button = self.selenium.find_element_by_id("addEmail")
        add_email_button.click()
        #check the email form-0 is displayed
        self.assertTrue(email_form_1.is_displayed())
        #check that email_form-0 is not marked as deleted and 'input[type=checkbox]' is hidden'
        delete_email_checkbox = self.selenium.find_element_by_id("id_emailaddress_set-0-DELETE")
        self.assertFalse(delete_email_checkbox.is_displayed())
        self.assertFalse(delete_email_checkbox.is_selected())
        #add the second email form
        add_email_button.click()
        #check the email form 1 is displayed
        self.assertTrue(email_form_2.is_displayed())
        #check that email_form-1 is not marked as deleted and 'input[type=checkbox]' is hidden
        delete_email_checkbox1 = self.selenium.find_element_by_id("id_emailaddress_set-1-DELETE")
        self.assertFalse(delete_email_checkbox1.is_displayed())        
        self.assertFalse(delete_email_checkbox1.is_selected())
        
        remove_button1 = self.selenium.find_element_by_xpath("//label[@for='id_emailaddress_set-0-DELETE']")
        remove_button2 = self.selenium.find_element_by_xpath("//label[@for='id_emailaddress_set-1-DELETE']")
        #remove first email form
        remove_button1.click()
        #check the email form-0 is not displayed
        self.assertFalse(email_form_1.is_displayed())
        #check that email_form-0 is marked as deleted
        self.assertTrue(delete_email_checkbox.is_selected())
        #remove second email form
        remove_button2.click()
        #check the email form-1 is not displayed
        self.assertFalse(email_form_2.is_displayed())
        #check that email_form-1 is marked as deleted
        self.assertTrue(delete_email_checkbox1.is_selected())
        
    def test_create_profile_add_remove_second_address_form(self):
        """
        Test that JS functions to add and remove second address form
        work as intended.
        """
        address_form_1 = self.selenium.find_element_by_id("address-form-0")
        address_form_2 = self.selenium.find_element_by_id("address-form-1")
        remove_button1 = self.selenium.find_element_by_xpath("//label[@for='id_address_set-0-DELETE']")
        remove_button2 = self.selenium.find_element_by_xpath("//label[@for='id_address_set-1-DELETE']")
        address_form_1_delete_checkbox = self.selenium.find_element_by_id("id_address_set-0-DELETE")
        address_form_2_delete_checkbox = self.selenium.find_element_by_id("id_address_set-1-DELETE")
        #check if first address form is displayed and not marked 'deleted'
        #by default
        self.assertTrue(address_form_1.is_displayed())
        #self.assertFalse(remove_button1.is_displayed())
        self.assertFalse(address_form_1_delete_checkbox.is_selected())
        #check if second address form is not displayed and marked as deleted
        #by default
        self.assertFalse(address_form_2.is_displayed())
        self.assertTrue(address_form_2_delete_checkbox.is_selected())
        #add an additional address form and left it empty                         
        add_address_button = self.selenium.find_element_by_id("addAddress")
        add_address_button.click()
        #check if second address form is displayed and not marked as 'deleted'
        self.assertTrue(address_form_2.is_displayed())
        self.assertTrue(remove_button2.is_displayed())
        self.assertFalse(address_form_2_delete_checkbox.is_selected())
        #remove second address form
        remove_button2.click()
        #check if second address form is not displayed and marked 'deleted'
        self.assertFalse(address_form_2.is_displayed())
        self.assertTrue(address_form_2_delete_checkbox.is_selected())
                                 
    def test_create_profile_types_switch(self):
        """
        Test JS functionality to switch types of email and addresses.
        """
        #add two email forms                           
        add_email_button = self.selenium.find_element_by_id("addEmail")
        add_email_button.click()
        add_email_button.click()
        #check initial types of email forms
        email_form_0_type_selector = self.selenium.find_element_by_id("id_emailaddress_set-0-email_type")
        email_form_1_type_selector = self.selenium.find_element_by_id("id_emailaddress_set-1-email_type")
        self.assertEqual(email_form_0_type_selector.get_attribute("value"), "CT")
        self.assertEqual(email_form_1_type_selector.get_attribute("value"), "PT")
        #change type of the first email form and check if a type of the second form changed as well
        Select(email_form_0_type_selector).select_by_value("PT")
        self.assertEqual(email_form_1_type_selector.get_attribute("value"), "CT")
        #try to change type of the second email form and check if types of both forms were not changed
        Select(email_form_1_type_selector).select_by_value("PT")
        self.assertEqual(email_form_0_type_selector.get_attribute("value"), "PT")
        self.assertEqual(email_form_1_type_selector.get_attribute("value"), "CT")
        
        #add an additional address form                         
        add_address_button = self.selenium.find_element_by_id("addAddress")
        add_address_button.click()
        #check initial types of address forms
        address_form_0_type_selector = self.selenium.find_element_by_id("id_address_set-0-address_type")
        address_form_1_type_selector = self.selenium.find_element_by_id("id_address_set-1-address_type")
        self.assertEqual(address_form_0_type_selector.get_attribute("value"), "DL")
        self.assertEqual(address_form_1_type_selector.get_attribute("value"), "BL")
        #change type of the first address form and check if a type of the second form changed as well
        Select(address_form_0_type_selector).select_by_value('BL')
        self.assertEqual(address_form_1_type_selector.get_attribute("value"), "DL")
        #change type of the second address form and check if types of both forms were not changed
        Select(address_form_1_type_selector).select_by_value('BL')
        self.assertEqual(address_form_0_type_selector.get_attribute("value"), "BL")
        self.assertEqual(address_form_1_type_selector.get_attribute("value"), "DL")
