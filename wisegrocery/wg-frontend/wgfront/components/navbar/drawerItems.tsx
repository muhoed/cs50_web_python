const drawerItemsAccount = [
    {
      key: 'SignIn',
      title: 'Sign In',
      routes: [{nav: 'MainDrawer', routeName: 'Login', title: 'Sign In'}],
    },
    {
      key: 'SignUp',
      title: 'Sign Up',
      routes: [{nav: 'MainDrawer', routeName: 'Register', title: 'Sign Up'}],
    },
];

const drawerItemsMain = [
    {
        key: 'Home',
        title: 'Home',
        routes: [
            {
                nav: 'MainDrawer', 
                routeName: 'Groceries', 
                title: 'Groceries', 
                parent: 'Home',
                routes: [
                    {nav: 'MainDrawer', routeName: 'Products', title: 'Products', parent: 'Groceries', routes: []},
                    {nav: 'MainDrawer', routeName: 'Shopping', title: 'Shopping', parent: 'Groceries', routes: []},
                    {nav: 'MainDrawer', routeName: 'Cooking', title: 'Cooking', parent: 'Groceries', routes: []},
                ]
            },
            {nav: 'MainDrawer', routeName: 'Equipment', title: 'Equipment', parent: 'Home', routes: []},
            {nav: 'MainDrawer', routeName: 'Stock', title: 'Stock', parent: 'Home', routes: []},
        ]
    },
    {
      key: 'Settings',
      title: 'Settings',
      routes: [{nav: 'MainDrawer', routeName: 'Settings', title: 'Settings', parent: 'Settings', routes: []}],
    },
    {
      key: 'Notifications',
      title: 'Notifications',
      routes: [{nav: 'MainDrawer', routeName: 'Notifications', title: 'Notifications', parent: 'Notifications', routes: []}],
    },
  ];

  export { drawerItemsAccount, drawerItemsMain };