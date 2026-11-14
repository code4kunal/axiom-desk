// The browser's only door to the capability registry: the httpOnly session cookie becomes the
// API's Bearer token here, so the browser never holds the token itself.
const SESSION_COOKIE = "__Host-axiom_session";

function sessionToken(cookieHeader: string | null): string | undefined {
  const prefix = `${SESSION_COOKIE}=`;
  return cookieHeader
    ?.split(/;\s*/)
    .find((c) => c.startsWith(prefix))
    ?.slice(prefix.length);
}

export async function POST(request: Request, { params }: { params: Promise<{ name: string }> }) {
  // The cookie is SameSite=Lax, so a cross-site form POST can still carry it; Origin must match.
  if (request.headers.get("origin") !== new URL(request.url).origin) {
    return Response.json({ error: "cross-origin request refused" }, { status: 403 });
  }
  const token = sessionToken(request.headers.get("cookie"));
  if (!token) return Response.json({ error: "signed out" }, { status: 401 });

  const { name } = await params;
  let upstream: Response;
  try {
    upstream = await fetch(`${process.env.AXIOM_API_ORIGIN}/capabilities/${encodeURIComponent(name)}`, {
      method: "POST",
      headers: {
        authorization: `Bearer ${token}`,
        "content-type": "application/json",
        "x-axiom-surface": "screen",
      },
      body: await request.text(),
      cache: "no-store",
    });
  } catch {
    return Response.json({ error: "API unreachable" }, { status: 502 }); // API down, refused, or no origin configured
  }
  return new Response(upstream.body, {
    status: upstream.status,
    headers: { "content-type": upstream.headers.get("content-type") ?? "application/json" },
  });
}
