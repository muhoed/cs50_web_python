import { useMediaQuery } from 'react-responsive'
import { Platform } from 'react-native'

let mobile = { maxWidth: 599 };
let tablet = { minWidth: 600, maxWidth: 999 };
let desktop = { minWidth: 1000 };
let mobileQuery: any = null;
let tabletQuery: any = null;
let desktopQuery: any = null;

if (Platform.OS !== 'web') {
  mobileQuery = { query: `(max-device-width: ${mobile.maxWidth}px)` };
  tabletQuery = { query: `(min-device-width: ${tablet.minWidth}px) and (max-device-width: ${tablet.maxWidth}px)` };
  desktopQuery = { query: `(min-device-width: ${desktop.minWidth}px)` };
}

export default function useScreenSize() {
    const isMobile = useMediaQuery(mobileQuery || mobile);
    const isTablet = useMediaQuery(tabletQuery || tablet);
    const isDesktop = useMediaQuery(desktopQuery || desktop);
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