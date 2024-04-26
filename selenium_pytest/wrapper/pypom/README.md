# PyPom

PyPom seeks to reduce the amount of boilerplate needed to write UI tests.

Note: The current version of SHIELD PyPom does not yet cover Appium.

Improvements
1. Automatic waits
2. Base Page class with open() and url encoding
3. Built in locator manipulation
4. PageSection base class to represent page sections


## Features

### Waiting for element state
 Many actions require an element to exist or be visible to perform, not as an expectation of your
 test but as a fundamental behavior of GUI interaction e.g., a button must be displayed
 before you can click it.

```
class MyPage(Page):
    submit_button = ByID('submit')


page = MyPage(driver)
page.submit_button.click()  # wait_until_visible performed automatically
```

### Locator parsing
```
login_form = ByID('some-form')
login_form.by  # 'id'
login_form.value  #  'some-form'
```

Available locators include:
* ByID
* ByName
* ByCss
* ByClass
* ByTag
* ByXPath
* ByLinkText
* ByPartialLinkText


### Locator combining

```
# mismatched locators coverted to ByCss automatically
# '+' operator acts as 'add as descendant'
login_form = ByID('some-form')
username_input = login_form + ByName('user_input')  #  ByCss('#some-form [name=user_input]')

```


### Base Page
The Page class initializes your locators with the driver and an optional timeout.
The Page class also offers an open() function that will get a url and encode query params.
```
class MyPage(Page):
    pass
    
page = MyPage(driver)
page.open('indeed.com/jobs', q='software engineer', l='london')
```


### Page Components
Consider the following html:
```html
<div>
    <body>
    <div id="top-nav">
       <form>
           <input>
           <button>Search</button>
       </form>
       <p>someone@indeed.com</p>
    </div>
    <div id="main">
        ...
    </div>
    </body>
</div>
```
The first div is a nav bar that's reused throughout the website, not just this page.
Instead of copying its selectors around, we can make a component.
```
class NavBar(PageSection):
    root = ById('top-nav')
    
    search_bar_input = ByTag('input')
    email_text = ByTag('p')
``` 

PageSection uses the special `root` class attribute 
to initialize all of its other locators as descendants of that root. No need to prepend
the root locator yourself. To take advantage of that auto-prepending, each locator must
be convertable to css. By default each locator class is already css-convertable 
except for ByXPath, ByLinkText, and ByPartialLinkText. Those three locators are still allowed but
will search the entire page source, not just the root element's children.
If you need to set the root element dynamically, you may pass it to the page as an `__init__` arg.
Doing so will shadow the static root attribute if one was specified.
