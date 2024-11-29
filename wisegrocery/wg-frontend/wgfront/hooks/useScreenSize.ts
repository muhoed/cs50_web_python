import { useMediaQuery } from 'react-responsive'
import { Platform } from 'react-native'

let mobile = { maxWidth: 599 };
let tablet = { minWidth: 600, maxWidth: 999 };
let desktop = { minWidth: 1000 };

if (Platform.OS !== 'web') {
  var mobileQuery = { query: `(max-device-width: ${mobile.maxWidth}px)` };
  var tabletQuery = { query: `(min-device-width: ${tablet.minWidth}px) and (max-device-width: ${tablet.maxWidth}px)` };
  var desktopQuery = { query: `(min-device-width: ${desktop.minWidth}px)` };
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