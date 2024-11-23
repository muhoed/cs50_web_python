import { useMediaQuery } from 'react-responsive'
import { Platform } from 'react-native'

let mobile = { maxWidth: 599 };
let tablet = { minWidth: 600, maxWidth: 999 };
let desktop = { minWidth: 1000 };

if (Platform.OS !== 'web') {
  mobile = { query: `(max-device-width: ${mobile.maxWidth}px)` };
  tablet = { query: `(min-device-width: ${tablet.minWidth}px) and (max-device-width: ${tablet.maxWidth}px)` };
  desktop = { query: `(min-device-width: ${desktop.minWidth}px)` };
}

export default function useScreenSize() {
    const isMobile = useMediaQuery(mobile);
    const isTablet = useMediaQuery(tablet);
    const isDesktop = useMediaQuery(desktop);
    const isPortrait = useMediaQuery({ query: '(orientation: portrait)' });
    return {
        isMobile,
        isTablet,
        isDesktop,
        isMobileOrTablet: isMobile || isTablet,
        isTabletOrDesktop: isTablet || isDesktop,
        isPortrait
    };
}