const MODULES = [
    {
      name: 'Groceries',
      text: 'Grocery inventories management',
      parent: 'Home',
    },
    {
      name: 'Products',
      text: 'Manage grocery products',
      parent: 'Groceries',
    },
    {
      name: 'ProductForm',
      text: 'Product details',
      parent: 'Products',
    },
    {
      name: 'Equipment',
      text: 'Manage your storage equipment',
      parent: 'Groceries',
    },
    {
      name: 'EquipmentForm',
      text: 'Equipment details',
      parent: 'Equipment',
    },
    {
      name: 'Stock',
      text: 'Review and manage groceries in-stock',
      parent: 'Groceries',
    },
    {
      name: 'Balances',
      text: 'Enter grocery stock balances',
      parent: 'Stock',
    },
    {
      name: 'ConversionRules',
      text: 'Configure conversion rules',
      parent: 'Stock',
    },
    {
      name: 'Shopping',
      text: 'Shopping planning',
      parent: "Home",
    },
    {
      name: 'Cooking',
      text: 'Cooking planning',
      parent: "Home",
    },
  ];

  export {MODULES};