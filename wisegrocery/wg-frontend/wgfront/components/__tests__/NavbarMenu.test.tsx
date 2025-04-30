import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import NavbarMenu from '../navbar/NavbarMenu'; // Adjust path
import { Platform } from 'react-native';

// --- Mocks ---

// Mock Redux hooks and actions
const mockDispatch = jest.fn();
const mockLogoutUser = jest.fn();
const mockSettingsReset = jest.fn();

jest.mock('@/hooks/useWGDispatch', () => ({
  useWGDispatch: () => mockDispatch,
}));

// Mock useWGSelector to simulate logged-in state
jest.mock('@/hooks/useWGSelector', () => ({
  useWGSelector: jest.fn().mockImplementation((selector: any) => {
    if (selector.toString().includes('state.secure.user.auth')) {
      return { authenticated: true }; // Simulate user is logged in
    }
    return undefined;
  }),
}));

jest.mock('@/store/redux/userSlice', () => ({
  logoutUser: () => mockLogoutUser(),
}));

jest.mock('@/store/redux/settingsSlice', () => ({
  settingsReset: () => mockSettingsReset(),
}));

// Mock expo-router (needed for Link components inside NavbarMenu)
jest.mock('expo-router', () => ({
  router: {
    push: jest.fn(), // Mock push if used by menu items
    navigate: jest.fn(), // Mock navigate if used
  },
  Link: ({ children, ...props }: any) => <>{children}</>, // Basic mock for Link
  Href: jest.fn(), // Mock Href type if needed
}));

// Mock react-native-paper components used
jest.mock('react-native-paper', () => {
  const ActualPaper = jest.requireActual('react-native-paper');
  return {
    ...ActualPaper,
    Appbar: { ...ActualPaper.Appbar, Action: jest.fn(() => null) }, // Mock Appbar.Action if used
    Searchbar: jest.fn(() => null), // Mock Searchbar
    useTheme: () => ({ colors: { primary: 'blue' } }), // Provide mock theme
  };
});

// Mock useScreenSize hook
jest.mock('../../hooks/useScreenSize', () => () => ({ isDesktop: true })); // Assume desktop for web test

// --- Tests ---

describe('<NavbarMenu />', () => {

  beforeEach(() => {
    mockDispatch.mockClear();
    mockLogoutUser.mockClear();
    mockSettingsReset.mockClear();
    // Reset selector mock for logged-in state
    const mockUseWGSelector = require('@/hooks/useWGSelector').useWGSelector;
    mockUseWGSelector.mockClear();
    mockUseWGSelector.mockImplementation((selector: any) => {
        if (selector.toString().includes('state.secure.user.auth')) {
            return { authenticated: true };
        }
        return undefined;
    });
    // Set platform to web for testing renderWebNav
    Platform.OS = 'web';
  });

  it('renders Logout button when user is authenticated (on web)', () => {
    const { getByText } = render(<NavbarMenu />);
    // Ensure it renders the web version
    expect(getByText('Logout')).toBeTruthy(); 
  });

  it('calls logoutUser and settingsReset on Logout press (on web)', async () => {
    const { getByText } = render(<NavbarMenu />);
    const logoutButton = getByText('Logout');

    fireEvent.press(logoutButton);

    // Check actions dispatched
    await waitFor(() => {
      expect(mockDispatch).toHaveBeenCalledTimes(2);
      expect(mockLogoutUser).toHaveBeenCalledTimes(1);
      expect(mockSettingsReset).toHaveBeenCalledTimes(1);
    });
  });

}); 