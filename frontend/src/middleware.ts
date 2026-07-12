/**
 * Edge middleware checks ONLY for the presence of the refresh cookie —
 * it cannot validate a JWT signature at the edge without shipping the
 * secret to the edge runtime, which we deliberately avoid. Real
 * authorization (is the token valid? what role?) happens server-side
 * per-request via api/deps.py. This middleware exists purely to stop
 * unauthenticated users from ever seeing the dashboard shell/flash of
 * protected content.
 */
import { NextResponse, type NextRequest } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard", "/vehicles", "/drivers", "/routes", "/trips", "/bookings", "/users"];
const REFRESH_COOKIE_NAME = "transitops_refresh_token";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some((p) => pathname.startsWith(p));

  if (!isProtected) return NextResponse.next();

  const hasSession = request.cookies.has(REFRESH_COOKIE_NAME);
  if (!hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/vehicles/:path*", "/drivers/:path*", "/routes/:path*", "/trips/:path*", "/bookings/:path*", "/users/:path*"],
};