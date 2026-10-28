"""Ready-written Rule Cards: every rule, theorem, technique or identity a video uses.

A day's step names the rule it uses with rule="key" (or a list of keys), and
IntegralVideo shows the card before that step the first time the rule appears in a
video, as card_kind() at the bottom decides (full, short or none), and a small corner
tag on later uses.

Each entry:
    name       plain words (maths, if any, in $...$)
    statement  a MathTex string (display maths, no $)
    symbols, when, why
               lists of cap(r"...") lines: at most 12 words each, each makes sense
               alone, all maths in $...$ with LaTeX commands

"why" must give the actual reason (u-substitution is the chain rule in reverse, ...).
check_text.py typesets and checks every line here. Add a new card the first time a
day needs a rule that is not here yet.
"""


def cap(text):
    """Caption marker (same as common.cap); check_text.py finds every cap(...) line."""
    return text


ALGEBRA = "algebra"         # rule="algebra": a step that only simplifies; no card

RULE_CARDS = {
    "power_rule": dict(
        name=r"The Power Rule",
        statement=r"\int x^{n}\,dx=\frac{x^{n+1}}{n+1}+C,\qquad n\neq -1",
        symbols=[cap(r"$n$ is fixed; $C$ is any constant.")],
        when=[cap(r"A power of the variable, like $t^{3}$.")],
        why=[cap(r"Differentiating $\frac{x^{n+1}}{n+1}$ gives back $x^{n}$.")],
    ),
    "linearity": dict(
        name=r"Linearity of the Integral",
        statement=r"\int \big(a\,f+b\,g\big)\,dx=a\!\int f\,dx+b\!\int g\,dx",
        symbols=[cap(r"$f$, $g$ are functions; $a$, $b$ are constants.")],
        when=[cap(r"A sum, or a constant factor.")],
        why=[cap(r"Scaling heights scales area; stacking heights adds areas.")],
    ),
    "constant_of_integration": dict(
        name=r"The Constant of Integration",
        statement=r"\frac{d}{dx}\big(F(x)+C\big)=F'(x)",
        symbols=[cap(r"$F$ is one antiderivative; $C$ is any constant.")],
        when=[cap(r"Every indefinite integral, one without limits, needs $+\,C$.")],
        why=[cap(r"A constant has derivative $0$, so it is invisible to $\frac{d}{dx}$."),
             cap(r"So every vertical shift of $F$ is also an answer.")],
    ),
    "exp_integral": dict(
        name=r"Integral of $e^{x}$",
        statement=r"\int e^{x}\,dx=e^{x}+C",
        symbols=[cap(r"$e\approx 2.718$ is Euler's number.")],
        when=[cap(r"$e^{x}$, or $e$ to a linear power.")],
        why=[cap(r"$e^{x}$ is its own derivative, so its own antiderivative.")],
    ),
    "reciprocal_integral": dict(
        name=r"Integral of $\frac{1}{x}$",
        statement=r"\int \frac{1}{x}\,dx=\ln|x|+C",
        symbols=[cap(r"$\ln$ is the natural logarithm, with base $e$.")],
        when=[cap(r"The integrand is $\frac{1}{x}$: the power rule fails for $n=-1$.")],
        why=[cap(r"The derivative of $\ln x$ is $\frac{1}{x}$ for $x>0$."),
             cap(r"The bars $|x|$ make it work for negative $x$ too.")],
    ),
    "sin_integral": dict(
        name=r"Integral of $\sin x$",
        statement=r"\int \sin x\,dx=-\cos x+C",
        symbols=[cap(r"$x$ is an angle measured in radians.")],
        when=[cap(r"The integrand is $\sin x$.")],
        why=[cap(r"The derivative of $\cos x$ is $-\sin x$."),
             cap(r"So $-\cos x$ has derivative $\sin x$.")],
    ),
    "cos_integral": dict(
        name=r"Integral of $\cos x$",
        statement=r"\int \cos x\,dx=\sin x+C",
        symbols=[cap(r"$x$ is an angle measured in radians.")],
        when=[cap(r"The integrand is $\cos x$.")],
        why=[cap(r"The derivative of $\sin x$ is $\cos x$, so undo it.")],
    ),
    "sec2_integral": dict(
        name=r"Integral of $\sec^{2}x$",
        statement=r"\int \sec^{2}x\,dx=\tan x+C",
        symbols=[cap(r"$\sec x=\frac{1}{\cos x}$, and $\tan x=\frac{\sin x}{\cos x}$.")],
        when=[cap(r"The integrand is $\sec^{2}x$, or $\frac{1}{\cos^{2}x}$.")],
        why=[cap(r"The quotient rule gives $\frac{d}{dx}\tan x=\frac{1}{\cos^{2}x}$."),
             cap(r"That is $\sec^{2}x$, so $\tan x$ is its antiderivative.")],
    ),
    "ftc": dict(
        name=r"The Fundamental Theorem of Calculus",
        statement=r"\int_{a}^{b} f(x)\,dx=F(b)-F(a),\qquad F'=f",
        symbols=[cap(r"$F$ is any antiderivative of $f$.")],
        when=[cap(r"A definite integral, once an antiderivative is known.")],
        why=[cap(r"Area grows at the rate of the curve's height.")],
    ),
    "u_substitution": dict(
        name=r"$u$-Substitution",
        statement=r"\int f\big(g(x)\big)\,g'(x)\,dx=\int f(u)\,du,\qquad u=g(x)",
        symbols=[cap(r"$u=g(x)$ is the inside; $du=g'(x)\,dx$.")],
        when=[cap(r"An inside function appears with its derivative.")],
        why=[cap(r"It is the chain rule in reverse.")],
    ),
    "change_of_limits": dict(
        name=r"Changing the Limits",
        statement=r"\int_{a}^{b} f\big(g(x)\big)\,g'(x)\,dx=\int_{g(a)}^{g(b)} f(u)\,du",
        symbols=[cap(r"Old limits $a,b$; new limits $g(a),g(b)$.")],
        when=[cap(r"Substituting in an integral with limits.")],
        why=[cap(r"$u=g(x)$ tracks $x$, so the ends move together.")],
    ),
    "integration_by_parts": dict(
        name=r"Integration by Parts",
        statement=r"\int u\,dv=uv-\int v\,du",
        symbols=[cap(r"$u$ is the part we differentiate, giving $du$."),
                 cap(r"$dv$ is the part we integrate, giving $v$.")],
        when=[cap(r"A product of two functions, one simpler when differentiated.")],
        why=[cap(r"It is the product rule, integrated on both sides."),
             cap(r"$(uv)'=u'v+uv'$, so $\int uv'=uv-\int u'v$.")],
    ),
    "partial_fractions": dict(
        name=r"Partial Fractions",
        statement=r"\frac{1}{(x-a)(x-b)}=\frac{A}{x-a}+\frac{B}{x-b}",
        symbols=[cap(r"$A$ and $B$ are constants we solve for.")],
        when=[cap(r"A fraction of polynomials whose bottom factors into pieces.")],
        why=[cap(r"Adding $\frac{A}{x-a}+\frac{B}{x-b}$ gives one fraction over that product."),
             cap(r"Running it backwards splits a hard fraction into easy logarithms.")],
    ),
    "pythagorean_identity": dict(
        name=r"The Pythagorean Identity",
        statement=r"\sin^{2}x+\cos^{2}x=1",
        symbols=[cap(r"$\sin^{2}x$ means $(\sin x)^{2}$.")],
        when=[cap(r"Squares of $\sin x$ or $\cos x$ that you want to swap.")],
        why=[cap(r"On the unit circle a point is $(\cos x,\sin x)$."),
             cap(r"Pythagoras: its distance from the centre is $1$.")],
    ),
    "double_angle": dict(
        name=r"Double Angle Identities",
        statement=r"\sin 2x=2\sin x\cos x,\qquad \cos 2x=\cos^{2}x-\sin^{2}x",
        symbols=[cap(r"$2x$ is twice the angle $x$.")],
        when=[cap(r"Products like $\sin x\cos x$, or squares like $\cos^{2}x$.")],
        why=[cap(r"Put $b=a$ in the angle-sum formulas for $\sin$ and $\cos$.")],
    ),
    "trig_substitution": dict(
        name=r"Trigonometric Substitution",
        statement=r"\sqrt{a^{2}-x^{2}}:\quad x=a\sin\theta,\quad dx=a\cos\theta\,d\theta",
        symbols=[cap(r"$a$ is a positive constant; $\theta$ is the new angle variable.")],
        when=[cap(r"A root like $\sqrt{a^{2}-x^{2}}$ in the integrand.")],
        why=[cap(r"Then $a^{2}-x^{2}=a^{2}\cos^{2}\theta$, a perfect square."),
             cap(r"The Pythagorean identity removes the square root.")],
    ),
    "log_laws": dict(
        name=r"Logarithm Laws",
        statement=r"\ln(ab)=\ln a+\ln b,\quad \ln\frac{a}{b}=\ln a-\ln b,\quad \ln a^{k}=k\ln a",
        symbols=[cap(r"$a,b>0$; $k$ is any number.")],
        when=[cap(r"Logarithms of products, quotients or powers.")],
        why=[cap(r"A logarithm is an exponent; exponents add when powers multiply.")],
    ),
    "exponent_laws": dict(
        name=r"Exponent Laws",
        statement=r"a^{m}a^{n}=a^{m+n},\quad \frac{a^{m}}{a^{n}}=a^{m-n},\quad (a^{m})^{n}=a^{mn}",
        symbols=[cap(r"$a>0$ is the base; $m,n$ are exponents.")],
        when=[cap(r"Powers of one base, multiplied, divided or raised.")],
        why=[cap(r"$a^{m}$ is $m$ copies of $a$; count the copies.")],
    ),
    "odd_even_symmetry": dict(
        name=r"Odd and Even Symmetry",
        statement=(r"\int_{-a}^{a} f(x)\,dx=\begin{cases}2\int_{0}^{a} f(x)\,dx & f\text{ even}\\"
                   r" 0 & f\text{ odd}\end{cases}"),
        symbols=[cap(r"Even: $f(-x)=f(x)$. Odd: $f(-x)=-f(x)$.")],
        when=[cap(r"Limits from $-a$ to $a$, symmetric about $0$.")],
        why=[cap(r"Even halves mirror each other; odd halves are opposite and cancel.")],
    ),
    "improper_integral": dict(
        name=r"Improper Integrals",
        statement=r"\int_{a}^{\infty} f(x)\,dx=\lim_{b\to\infty}\int_{a}^{b} f(x)\,dx",
        symbols=[cap(r"$b$ is a finite upper limit that we let grow.")],
        when=[cap(r"A limit is $\infty$, or the integrand blows up somewhere.")],
        why=[cap(r"We cannot integrate to $\infty$ directly."),
             cap(r"So integrate to $b$, then see what happens as $b\to\infty$.")],
    ),
    "laplace_transform": dict(
        name=r"The Laplace Transform",
        statement=r"\mathcal{L}\{f\}(s)=\int_{0}^{\infty} e^{-st}f(t)\,dt",
        symbols=[cap(r"$t$ is time; $s$ is a new variable; $\mathcal{L}$ names the transform.")],
        when=[cap(r"An integral of $e^{-st}$ times a function from $0$ to $\infty$.")],
        why=[cap(r"The factor $e^{-st}$ shrinks fast, so the integral is finite."),
             cap(r"Known transforms, like $\mathcal{L}\{1\}=\frac{1}{s}$, give answers instantly.")],
    ),
    "interval_additivity": dict(
        name=r"Splitting the Interval",
        statement=r"\int_{a}^{c} f(x)\,dx=\int_{a}^{b} f(x)\,dx+\int_{b}^{c} f(x)\,dx",
        symbols=[cap(r"$b$ is any split point between $a$ and $c$.")],
        when=[cap(r"The integrand has a different formula on different pieces.")],
        why=[cap(r"The area from $a$ to $c$ is two areas side by side.")],
    ),
    "ln_derivative": dict(
        name=r"Derivative of $\ln x$",
        statement=r"\frac{d}{dx}\ln x=\frac{1}{x},\qquad x>0",
        symbols=[cap(r"$\ln x$ is the power of $e$ giving $x$.")],
        when=[cap(r"Differentiating a logarithm.")],
        why=[cap(r"With $y=\ln x$, $\frac{dx}{dy}=x$, so $\frac{dy}{dx}=\frac{1}{x}$.")],
    ),
    "log_values": dict(
        name=r"Two Logarithm Values",
        statement=r"\ln 1=0,\qquad \ln e=1",
        symbols=[cap(r"$\ln$ has base $e\approx 2.718$.")],
        when=[cap(r"Limits at $1$ or $e$.")],
        why=[cap(r"$e^{0}=1$ and $e^{1}=e$.")],
    ),
    "absolute_value": dict(
        name=r"Absolute Value",
        statement=r"|w|=\begin{cases}w & w\ge 0\\ -w & w<0\end{cases}",
        symbols=[cap(r"$|w|$ is the distance of $w$ from $0$.")],
        when=[cap(r"Bars around an expression that can change sign.")],
        why=[cap(r"Distance is never negative, so a negative $w$ flips to $-w$.")],
    ),
    "product_rule": dict(
        name=r"The Product Rule",
        statement=r"\big(f\,g\big)'=f'\,g+f\,g'",
        symbols=[cap(r"$f'$ is the derivative of $f$.")],
        when=[cap(r"A product, or $f'g+fg'$ inside an integral.")],
        why=[cap(r"A rectangle $f$ by $g$ grows on two sides.")],
    ),
    "chain_rule": dict(
        name=r"The Chain Rule",
        statement=r"\frac{d}{dx}f\big(g(x)\big)=f'\big(g(x)\big)\,g'(x)",
        symbols=[cap(r"$g$ is inside; $f$ is outside.")],
        when=[cap(r"A function of a function, like $\ln(x+1)$.")],
        why=[cap(r"Rates multiply: $f$ reacts to $g$, $g$ to $x$.")],
    ),
    "quotient_rule": dict(
        name=r"The Quotient Rule",
        statement=r"\Big(\frac{f}{g}\Big)'=\frac{f'g-fg'}{g^{2}}",
        symbols=[cap(r"$f$ is the top, $g$ the bottom.")],
        when=[cap(r"Differentiating a fraction.")],
        why=[cap(r"$\frac{f}{g}=f\cdot g^{-1}$: product rule plus chain rule.")],
    ),
    "exp_derivative": dict(
        name=r"Derivative of $e^{x}$",
        statement=r"\frac{d}{dx}e^{x}=e^{x}",
        symbols=[cap(r"$e\approx 2.718$ is Euler's number.")],
        when=[cap(r"Differentiating $e^{x}$.")],
        why=[cap(r"Only base $e$ grows at exactly its own height.")],
    ),
    "exp_log_inverse": dict(
        name=r"$e^{x}$ and $\ln x$ Undo Each Other",
        statement=r"e^{\ln a}=a,\qquad \ln\big(e^{b}\big)=b",
        symbols=[cap(r"$a>0$; $b$ is any number.")],
        when=[cap(r"A variable trapped in a logarithm or exponent.")],
        why=[cap(r"$\ln a$ is the power of $e$ giving $a$.")],
    ),
    "nested_fixed_point": dict(
        name=r"Infinite Nested Expressions",
        statement=r"y=g\big(g(g(\cdots))\big)\quad\Longrightarrow\quad y=g(y)",
        symbols=[cap(r"$g$ is the step repeated forever.")],
        when=[cap(r"An expression that repeats inside itself.")],
        why=[cap(r"Peel one layer: the same tail, $y$, remains."),
             cap(r"Of two roots, the limit has $|g'(y)|<1$.")],
    ),
    "volume_of_revolution": dict(
        name=r"Volume of Revolution",
        statement=r"V=\pi\int_{a}^{b} y^{2}\,dx",
        symbols=[cap(r"$y=f(x)$ is the curve spun about the $x$-axis.")],
        when=[cap(r"A curve turned a full circle about the $x$-axis.")],
        why=[cap(r"Each thin slice is a disc of area $\pi y^{2}$.")],
    ),
    "reflection_property": dict(
        name=r"Reflecting the Variable",
        statement=r"\int_{-a}^{a} f(x)\,dx=\int_{-a}^{a} f(-x)\,dx",
        symbols=[cap(r"$f(-x)$ is the graph of $f$ mirrored in the $y$-axis.")],
        when=[cap(r"Limits symmetric about $0$, but $f$ neither odd nor even.")],
        why=[cap(r"A mirror image of a region has the same area.")],
    ),
    "cosh_definition": dict(
        name=r"Hyperbolic Cosine",
        statement=r"\cosh x=\frac{e^{x}+e^{-x}}{2}",
        symbols=[cap(r"$\cosh$ is the hyperbolic cosine.")],
        when=[cap(r"$\cosh x$ appears next to $e^{x}$ or $e^{-x}$.")],
        why=[cap(r"It is defined as the average of $e^{x}$ and $e^{-x}$.")],
    ),
    "completing_the_square": dict(
        name=r"Completing the Square",
        statement=r"x^{2}+2bx+c=(x+b)^{2}+\big(c-b^{2}\big)",
        symbols=[cap(r"$b$ is half the coefficient of $x$.")],
        when=[cap(r"A quadratic that does not factorise nicely.")],
        why=[cap(r"Expanding $(x+b)^{2}$ gives $x^{2}+2bx+b^{2}$; fix the constant.")],
    ),
    "arctan_integral": dict(
        name=r"Integral of $\frac{1}{1+x^{2}}$",
        statement=r"\int \frac{1}{1+x^{2}}\,dx=\tan^{-1}x+C",
        symbols=[cap(r"$\tan^{-1}x$ is the angle, in radians, whose tangent is $x$.")],
        when=[cap(r"One over $1$ plus a square, after completing the square.")],
        why=[cap(r"With $y=\tan^{-1}x$, $\frac{dx}{dy}=\sec^{2}y=1+x^{2}$."),
             cap(r"So $\frac{dy}{dx}=\frac{1}{1+x^{2}}$: undo it.")],
    ),
    "compound_angle": dict(
        name=r"Compound Angle Formula",
        statement=r"\cos(A-B)=\cos A\cos B+\sin A\sin B",
        symbols=[cap(r"$A$ and $B$ are any two angles.")],
        when=[cap(r"A sum like $\cos x+\sin x$, to merge into one cosine.")],
        why=[cap(r"Rotating by $A$ then back by $B$ is rotating by $A-B$.")],
    ),
    "sine_addition": dict(
        name=r"Sine of a Sum",
        statement=r"\sin(A+B)=\sin A\cos B+\cos A\sin B",
        symbols=[cap(r"$A$ and $B$ are any two angles.")],
        when=[cap(r"$\sin$ of an angle plus a constant, like $x+\frac{\pi}{4}$.")],
        why=[cap(r"Rotating by $B$ then by $A$ is rotating by $A+B$.")],
    ),
    "kings_rule": dict(
        name=r"Reflecting in the Middle",
        statement=r"\int_{0}^{a} f(x)\,dx=\int_{0}^{a} f(a-x)\,dx",
        symbols=[cap(r"$f(a-x)$ is $f$ mirrored in the line $x=\frac{a}{2}$.")],
        when=[cap(r"An integrand containing $a-x$, on limits $0$ to $a$.")],
        why=[cap(r"The substitution $u=a-x$ swaps the ends; a mirror keeps area.")],
    ),
    "interval_reflection": dict(
        name=r"Reflecting the Interval",
        statement=r"\int_{a}^{b} f(x)\,dx=\int_{a}^{b} f(a+b-x)\,dx",
        symbols=[cap(r"$f(a+b-x)$ is $f$ mirrored in the midpoint $x=\frac{a+b}{2}$.")],
        when=[cap(r"An integrand containing $a+b-x$, on limits $a$ to $b$.")],
        why=[cap(r"The substitution $u=a+b-x$ swaps the ends; a mirror keeps area.")],
    ),
    "csc2_integral": dict(
        name=r"Integral of $\csc^{2}x$",
        statement=r"\int \csc^{2}x\,dx=-\cot x+C",
        symbols=[cap(r"$\csc x=\frac{1}{\sin x}$, and $\cot x=\frac{\cos x}{\sin x}$.")],
        when=[cap(r"The integrand is $\csc^{2}x$, or $\frac{1}{\sin^{2}x}$.")],
        why=[cap(r"The quotient rule gives $\frac{d}{dx}\cot x=-\csc^{2}x$.")],
    ),
    "tan_substitution": dict(
        name=r"Substituting $x=\tan\theta$",
        statement=r"x=\tan\theta,\qquad dx=\sec^{2}\theta\,d\theta=(1+x^{2})\,d\theta",
        symbols=[cap(r"$\theta$ is the new angle variable.")],
        when=[cap(r"A factor $1+x^{2}$ in the integrand.")],
        why=[cap(r"$\frac{d}{d\theta}\tan\theta=\sec^{2}\theta=1+\tan^{2}\theta$, so $1+x^{2}$ cancels.")],
    ),
    "tan_triple_angle": dict(
        name=r"Triple Angle Formula for $\tan$",
        statement=r"\tan 3\theta=\frac{3\tan\theta-\tan^{3}\theta}{1-3\tan^{2}\theta}",
        symbols=[cap(r"$3\theta$ is three times the angle $\theta$.")],
        when=[cap(r"A cubic over a quadratic in $\tan\theta$ of this shape.")],
        why=[cap(r"Apply the $\tan$ angle-sum formula to $2\theta+\theta$.")],
    ),
    "tan_integral": dict(
        name=r"Integral of $\tan x$",
        statement=r"\int \tan x\,dx=-\ln|\cos x|+C",
        symbols=[cap(r"$\tan x=\frac{\sin x}{\cos x}$.")],
        when=[cap(r"The integrand is $\tan x$, or $\tan$ of a multiple of $x$.")],
        why=[cap(r"The top $\sin x$ is minus the derivative of the bottom.")],
    ),
    "quadratic_formula": dict(
        name=r"The Quadratic Formula",
        statement=r"ay^{2}+by+c=0\quad\Longrightarrow\quad y=\frac{-b\pm\sqrt{b^{2}-4ac}}{2a}",
        symbols=[cap(r"$a\neq 0$, $b$ and $c$ are the coefficients.")],
        when=[cap(r"A quadratic equation that does not factorise nicely.")],
        why=[cap(r"It is completing the square, done once for every quadratic.")],
    ),
    "midpoint_symmetry": dict(
        name=r"Symmetry About the Midpoint",
        statement=r"f(a+b-x)=f(x)\quad\Longrightarrow\quad\int_{a}^{b} f(x)\,dx=2\int_{a}^{\frac{a+b}{2}} f(x)\,dx",
        symbols=[cap(r"$\frac{a+b}{2}$ is the midpoint of $a$ and $b$.")],
        when=[cap(r"The curve is its own mirror image about the midpoint.")],
        why=[cap(r"Mirroring the left half gives the right half: equal areas.")],
    ),
    "sec_reciprocal": dict(
        name=r"Reciprocal Trig Functions",
        statement=r"\sec x=\frac{1}{\cos x},\qquad \frac{1}{\sec x}=\cos x",
        symbols=[cap(r"$\sec x$ is the secant of the angle $x$.")],
        when=[cap(r"$\sec x$ appears, especially in a denominator.")],
        why=[cap(r"$\sec$ is defined as one over $\cos$.")],
    ),
    "small_angle_limits": dict(
        name=r"Small Angle Limits",
        statement=r"\lim_{n\to 0}\frac{\sin n}{n}=1,\qquad \lim_{n\to 0}\frac{1-\cos n}{n}=0",
        symbols=[cap(r"$n$ is an angle in radians, shrinking to $0$.")],
        when=[cap(r"$\sin n$ or $1-\cos n$ divided by a small $n$.")],
        why=[cap(r"For small $n$, $\sin n\approx n$ and $1-\cos n\approx\frac{n^{2}}{2}$.")],
    ),
    "straight_line": dict(
        name=r"Equation of a Straight Line",
        statement=r"m=\frac{y_{2}-y_{1}}{x_{2}-x_{1}},\qquad y-y_{1}=m\,(x-x_{1})",
        symbols=[cap(r"$m$ is the gradient; $(x_{1},y_{1})$ is a point on the line.")],
        when=[cap(r"A line given by two points on it.")],
        why=[cap(r"A straight line rises by $m$ for every $1$ across.")],
    ),
    "area_between_curves": dict(
        name=r"Area Between Two Graphs",
        statement=r"A=\int_{a}^{b}\big(\text{top}-\text{bottom}\big)\,dx",
        symbols=[cap(r"Top and bottom are the upper and lower boundaries.")],
        when=[cap(r"A region bounded above and below by two graphs.")],
        why=[cap(r"Each thin strip has height top minus bottom.")],
    ),
    "washer_method": dict(
        name=r"Volume With a Hole: Washers",
        statement=r"V=\pi\int_{a}^{b}\big(R^{2}-r^{2}\big)\,dx",
        symbols=[cap(r"$R$ is the outer radius; $r$ is the inner radius.")],
        when=[cap(r"A region between two curves spun about the $x$-axis.")],
        why=[cap(r"Each slice is a disc of radius $R$ minus a hole.")],
    ),
    "trig_derivatives": dict(
        name=r"Derivatives of $\tan x$ and $\sec x$",
        statement=r"\frac{d}{dx}\tan x=\sec^{2}x,\qquad \frac{d}{dx}\sec x=\sec x\tan x",
        symbols=[cap(r"$\sec x=\frac{1}{\cos x}$, and $\tan x=\frac{\sin x}{\cos x}$.")],
        when=[cap(r"Differentiating $\tan x$ or $\sec x$.")],
        why=[cap(r"The quotient rule on $\frac{\sin x}{\cos x}$ and $\frac{1}{\cos x}$.")],
    ),
    "sec_tan_identity": dict(
        name=r"The $\sec$ and $\tan$ Identity",
        statement=r"\sec^{2}x-\tan^{2}x=1",
        symbols=[cap(r"$\sec^{2}x$ means $(\sec x)^{2}$.")],
        when=[cap(r"$\sec x$ and $\tan x$ appear together.")],
        why=[cap(r"Divide $\sin^{2}x+\cos^{2}x=1$ by $\cos^{2}x$.")],
    ),
    "average_value": dict(
        name=r"Average Value of a Function",
        statement=r"\bar{y}=\frac{1}{b-a}\int_{a}^{b} f(x)\,dx",
        symbols=[cap(r"$\bar{y}$ is the average height of $f$ on $[a,b]$.")],
        when=[cap(r"The mean value of a function over an interval.")],
        why=[cap(r"A rectangle of height $\bar{y}$ and width $b-a$ has the same area."),
             cap(r"So the area divided by the width is the average height.")],
    ),
    "reversing_limits": dict(
        name=r"Swapping the Limits",
        statement=r"\int_{b}^{a} f(x)\,dx=-\int_{a}^{b} f(x)\,dx",
        symbols=[cap(r"$a$ is the lower limit and $b$ the upper limit.")],
        when=[cap(r"A substitution leaves the limits upside down.")],
        why=[cap(r"$F(a)-F(b)$ is minus $F(b)-F(a)$.")],
    ),
    "tan_subtraction": dict(
        name=r"Tangent of a Difference",
        statement=r"\tan(A-B)=\frac{\tan A-\tan B}{1+\tan A\tan B}",
        symbols=[cap(r"$A$ and $B$ are any angles where $\tan$ is defined.")],
        when=[cap(r"$\tan$ of an angle minus a constant, like $\frac{\pi}{4}-\theta$.")],
        why=[cap(r"Divide the $\sin(A-B)$ formula by the $\cos(A-B)$ formula.")],
    ),
    "floor_function": dict(
        name=r"The Floor Function",
        statement=r"\lfloor y\rfloor=n\quad\Longleftrightarrow\quad n\le y<n+1,\ \ n\in\mathbb{Z}",
        symbols=[cap(r"$\lfloor y\rfloor$ is $y$ rounded down to a whole number.")],
        when=[cap(r"Brackets $\lfloor\ \rfloor$ around an expression.")],
        why=[cap(r"It is constant between whole numbers and jumps at each one.")],
    ),
    "divisor_sum": dict(
        name=r"Adding Up All Divisors",
        statement=r"\sum_{d\mid p^{a}q^{b}} d=\big(1+p+\cdots+p^{a}\big)\big(1+q+\cdots+q^{b}\big)",
        symbols=[cap(r"$d\mid N$ means $d$ divides $N$ exactly; $p$, $q$ are primes.")],
        when=[cap(r"A sum over every divisor of a number with known prime factors.")],
        why=[cap(r"Every divisor is one $p^{i}q^{j}$, with $0\le i\le a$ and $0\le j\le b$."),
             cap(r"Expanding the product lists each $p^{i}q^{j}$ exactly once."),
             cap(r"So there are $(a+1)(b+1)$ divisors.")],
    ),
    "cosh_sinh_exp": dict(
        name=r"$\cosh$ and $\sinh$ as Exponentials",
        statement=r"\cosh x+\sinh x=e^{x},\qquad \cosh x-\sinh x=e^{-x}",
        symbols=[cap(r"$\cosh x=\frac{e^{x}+e^{-x}}{2}$ and $\sinh x=\frac{e^{x}-e^{-x}}{2}$.")],
        when=[cap(r"$\cosh x$ and $\sinh x$ added or subtracted.")],
        why=[cap(r"Add or subtract the definitions: one exponential cancels.")],
    ),
    "euler_formula": dict(
        name=r"Euler's Formula",
        statement=r"e^{i\theta}=\cos\theta+i\sin\theta",
        symbols=[cap(r"$i^{2}=-1$; $\theta$ is a real angle in radians.")],
        when=[cap(r"An exponential with an imaginary power.")],
        why=[cap(r"The series for $e^{i\theta}$ splits into those of $\cos$ and $\sin$.")],
    ),
    "contour_shift": dict(
        name=r"Shifting the Line of Integration",
        statement=r"\int_{-\infty}^{\infty} e^{-(x+ic)^{2}}\,dx=\int_{-\infty}^{\infty} e^{-x^{2}}\,dx",
        symbols=[cap(r"$c$ is a real constant; $x+ic$ runs along a horizontal line.")],
        when=[cap(r"A Gaussian whose centre has moved off the real axis.")],
        why=[cap(r"$e^{-z^{2}}$ has no poles, so its integral around a rectangle is $0$."),
             cap(r"The short ends shrink to $0$ as the rectangle widens."),
             cap(r"So the shifted line and the real line give equal integrals.")],
    ),
    "gaussian_integral": dict(
        name=r"The Gaussian Integral",
        statement=r"\int_{-\infty}^{\infty} e^{-x^{2}}\,dx=\sqrt{\pi}",
        symbols=[cap(r"$e^{-x^{2}}$ is the bell curve.")],
        when=[cap(r"A full bell curve $e^{-x^{2}}$ from $-\infty$ to $\infty$.")],
        why=[cap(r"Its square is a double integral of $e^{-(x^{2}+y^{2})}$."),
             cap(r"In polar coordinates that is $\int_{0}^{2\pi}\int_{0}^{\infty} e^{-r^{2}}r\,dr\,d\theta=\pi$.")],
    ),
    "weierstrass_substitution": dict(
        name=r"The $t=\tan\frac{x}{2}$ Substitution",
        statement=r"t=\tan\frac{x}{2}:\quad \sin x=\frac{2t}{1+t^{2}},\quad dx=\frac{2\,dt}{1+t^{2}}",
        symbols=[cap(r"$t$ is the new variable; also $\cos x=\frac{1-t^{2}}{1+t^{2}}$.")],
        when=[cap(r"A fraction built from $\sin x$ and $\cos x$.")],
        why=[cap(r"$\sin x=2\sin\frac{x}{2}\cos\frac{x}{2}=\frac{2\tan\frac{x}{2}}{\sec^{2}\frac{x}{2}}$, and $\sec^{2}\frac{x}{2}=1+t^{2}$.")],
    ),
    "differentiation_under_integral": dict(
        name=r"Differentiating Under the Integral Sign",
        statement=r"\frac{d}{da}\int_{p}^{q} f(x,a)\,dx=\int_{p}^{q}\frac{\partial f}{\partial a}(x,a)\,dx",
        symbols=[cap(r"$a$ is a parameter; $\frac{\partial f}{\partial a}$ holds $x$ fixed.")],
        when=[cap(r"An integral that gets easier once its parameter is differentiated.")],
        why=[cap(r"An integral is a limit of sums; differentiate each term."),
             cap(r"This is allowed when $\frac{\partial f}{\partial a}$ is continuous.")],
    ),
    "analytic_continuation": dict(
        name=r"Extending a Formula to Complex Values",
        statement=r"f(a)=g(a)\ \text{for real } a\quad\Longrightarrow\quad f(a)=g(a)\ \text{for complex } a",
        symbols=[cap(r"$f$ and $g$ are analytic: smooth in $a$ as complex functions.")],
        when=[cap(r"A formula proved for real $a$, needed at a complex $a$.")],
        why=[cap(r"An analytic function is fixed by its values on an interval."),
             cap(r"So $f-g$, zero on the real line, is zero everywhere.")],
    ),
    "sum_of_squares_complex": dict(
        name=r"Factorising a Sum of Squares",
        statement=r"1+y^{2}=(1+iy)(1-iy)",
        symbols=[cap(r"$i$ is the imaginary unit, with $i^{2}=-1$.")],
        when=[cap(r"One plus a square, like $1+\sin^{4}x$, that will not factorise.")],
        why=[cap(r"Expanding gives $1-i^{2}y^{2}=1+y^{2}$.")],
    ),
    "conjugate_product": dict(
        name=r"A Number Times Its Conjugate",
        statement=r"z\,\bar{z}=|z|^{2}=x^{2}+y^{2},\qquad z=x+iy",
        symbols=[cap(r"$\bar{z}=x-iy$ is the conjugate of $z$.")],
        when=[cap(r"A product of two conjugate complex numbers.")],
        why=[cap(r"$(x+iy)(x-iy)=x^{2}-i^{2}y^{2}=x^{2}+y^{2}$.")],
    ),
    "hyperbolic_double_angle": dict(
        name=r"Hyperbolic Double Angles",
        statement=r"\sinh 2x=2\sinh x\cosh x,\qquad \cosh 2x=1+2\sinh^{2}x",
        symbols=[cap(r"$\sinh x=\frac{e^{x}-e^{-x}}{2}$ and $\cosh x=\frac{e^{x}+e^{-x}}{2}$.")],
        when=[cap(r"$\tanh$, $\sinh$ or $\cosh$ of $2x$ beside the same of $x$.")],
        why=[cap(r"Write both sides with exponentials: they match term by term.")],
    ),
    "sech_cosine_transform": dict(
        name=r"The Cosine Transform of $\operatorname{sech}$",
        statement=r"\operatorname{sech}t=\int_{0}^{\infty}\operatorname{sech}\frac{\pi\omega}{2}\,\cos\omega t\,d\omega",
        symbols=[cap(r"$\omega$ is a frequency; $\cos\omega t$ is a wave in $t$.")],
        when=[cap(r"$\operatorname{sech}t$ where cosine waves would be easier.")],
        why=[cap(r"$\operatorname{sech}$ is its own Fourier transform, up to scaling.")],
    ),
    "swap_order": dict(
        name=r"Swapping the Order of Integration",
        statement=r"\int_{0}^{\infty}\!\!\int_{0}^{\infty} f\,dt\,d\omega=\int_{0}^{\infty}\!\!\int_{0}^{\infty} f\,d\omega\,dt",
        symbols=[cap(r"$f(\omega,t)$ is a function of two variables.")],
        when=[cap(r"A double integral easier in the other order.")],
        why=[cap(r"Both orders add up the same volume, if $f\ge 0$ or $\int\!\!\int|f|<\infty$.")],
    ),
    "one_minus_cos_integral": dict(
        name=r"The Integral of $\frac{1-\cos at}{t^{2}}$",
        statement=r"\int_{0}^{\infty}\frac{1-\cos at}{t^{2}}\,dt=\frac{\pi a}{2},\qquad a\ge 0",
        symbols=[cap(r"$a$ is a fixed frequency; $t$ is the variable.")],
        when=[cap(r"$1-\cos at$ over $t^{2}$, from $0$ to $\infty$.")],
        why=[cap(r"By parts it is $a\int_{0}^{\infty}\frac{\sin at}{t}\,dt$, and that is $a\cdot\frac{\pi}{2}$.")],
    ),
    "geometric_series": dict(
        name=r"Geometric Series",
        statement=r"\frac{1}{1-r}=\sum_{n=0}^{\infty}r^{n},\qquad |r|<1",
        symbols=[cap(r"$r$ is the common ratio between terms.")],
        when=[cap(r"A fraction $\frac{1}{1-r}$ with a ratio $|r|<1$.")],
        why=[cap(r"$(1-r)(1+r+\cdots+r^{N})=1-r^{N+1}$, and $r^{N+1}\to 0$.")],
    ),
    "catalan_constant": dict(
        name=r"Catalan's Constant",
        statement=r"G=\sum_{n=0}^{\infty}\frac{(-1)^{n}}{(2n+1)^{2}}=1-\frac{1}{9}+\frac{1}{25}-\cdots\approx 0.9160",
        symbols=[cap(r"$G$ is a named constant, like $\pi$ or $e$.")],
        when=[cap(r"An alternating sum of one over the odd squares.")],
        why=[cap(r"No simpler closed form is known.")],
    ),
    "log_cosine_series": dict(
        name=r"The Fourier Series of a Log of Cosines",
        statement=r"\ln(1+2r\cos\psi+r^{2})=2\sum_{n=1}^{\infty}\frac{(-1)^{n+1}r^{n}}{n}\cos n\psi,\qquad |r|<1",
        symbols=[cap(r"$r$ is fixed with $|r|<1$; $\psi$ is any angle.")],
        when=[cap(r"A logarithm of $a+b\cos\psi$, with $a>|b|$.")],
        why=[cap(r"$1+2r\cos\psi+r^{2}=|1+re^{i\psi}|^{2}$: expand $\ln(1+re^{i\psi})$.")],
    ),
    "dilogarithm": dict(
        name=r"The Dilogarithm and Landen's Identity",
        statement=(r"\operatorname{Li}_{2}(z)=\sum_{n=1}^{\infty}\frac{z^{n}}{n^{2}},\qquad"
                   r" \operatorname{Li}_{2}(z)+\operatorname{Li}_{2}\Big(\frac{z}{z-1}\Big)=-\frac{1}{2}\ln^{2}(1-z)"),
        symbols=[cap(r"$z$ is a complex number with $|z|\le 1$.")],
        when=[cap(r"A sum of powers over squares, $\sum\frac{z^{n}}{n^{2}}$.")],
        why=[cap(r"Differentiate both sides in $z$: they agree, and match at $z=0$.")],
    ),
    "inverse_trig_sum": dict(
        name=r"$\sin^{-1}x$ and $\cos^{-1}x$ Add to $\frac{\pi}{2}$",
        statement=r"\sin^{-1}x+\cos^{-1}x=\frac{\pi}{2},\qquad -1\le x\le 1",
        symbols=[cap(r"$\sin^{-1}x$ is the angle in $[-\frac{\pi}{2},\frac{\pi}{2}]$ whose sine is $x$.")],
        when=[cap(r"Both $\sin^{-1}x$ and $\cos^{-1}x$ appear together.")],
        why=[cap(r"If $\sin\theta=x$, then $\cos\big(\frac{\pi}{2}-\theta\big)=x$ too.")],
    ),
    "arcsin_derivative": dict(
        name=r"Derivative of $\sin^{-1}x$",
        statement=r"\frac{d}{dx}\sin^{-1}x=\frac{1}{\sqrt{1-x^{2}}},\qquad -1<x<1",
        symbols=[cap(r"$\sin^{-1}x$ is the angle whose sine is $x$.")],
        when=[cap(r"Differentiating $\sin^{-1}x$, often inside integration by parts.")],
        why=[cap(r"Differentiate $\sin y=x$: $\cos y\,y'=1$, and $\cos y=\sqrt{1-x^{2}}$.")],
    ),
    "csc_integral": dict(
        name=r"Integral of $\csc\theta$",
        statement=r"\int\csc\theta\,d\theta=-\ln|\csc\theta+\cot\theta|+C",
        symbols=[cap(r"$\csc\theta=\frac{1}{\sin\theta}$ and $\cot\theta=\frac{\cos\theta}{\sin\theta}$.")],
        when=[cap(r"The integrand is $\csc\theta$, or $\frac{1}{\sin\theta}$.")],
        why=[cap(r"Times $\frac{\csc\theta+\cot\theta}{\csc\theta+\cot\theta}$: the top is minus the bottom's derivative.")],
    ),
    "summation_by_parts": dict(
        name=r"Summation by Parts",
        statement=r"\sum_{n=1}^{N}n\,(a_{n}-a_{n-1})=N a_{N}-\sum_{n=0}^{N-1}a_{n}",
        symbols=[cap(r"$a_{0},a_{1},a_{2},\dots$ is any sequence of numbers.")],
        when=[cap(r"A sum of $n$ times a difference of neighbouring terms.")],
        why=[cap(r"Each $a_{n}$ appears with $n$ and with $-(n+1)$: net $-1$.")],
    ),
    "telescoping_product": dict(
        name=r"Telescoping Products",
        statement=r"\prod_{n=1}^{N}\frac{b_{n-1}}{b_{n}}=\frac{b_{0}}{b_{N}}",
        symbols=[cap(r"$\prod$ multiplies the terms, as $\sum$ adds them.")],
        when=[cap(r"Each factor is a ratio of neighbouring terms.")],
        why=[cap(r"Each bottom $b_{n}$ cancels the same $b_{n}$ on the next top.")],
    ),
    "heaviside_step": dict(
        name=r"The Heaviside Step Function",
        statement=r"H(t)=\begin{cases}1, & t>0\\ 0, & t<0\end{cases}",
        symbols=[cap(r"$t$ is any real number; one point never changes an integral.")],
        when=[cap(r"A switch inside an integral that is either on or off.")],
        why=[cap(r"Integrating $1$ where it is on, $0$ elsewhere, gives a length.")],
    ),
    "sin_cos_derivatives": dict(
        name=r"Derivatives of $\sin x$ and $\cos x$",
        statement=r"\frac{d}{dx}\sin x=\cos x,\qquad \frac{d}{dx}\cos x=-\sin x",
        symbols=[cap(r"$x$ is an angle in radians.")],
        when=[cap(r"Differentiating any expression built from $\sin x$ and $\cos x$.")],
        why=[cap(r"For small $h$, $\sin h\approx h$ and $\cos h\approx 1$ in radians.")],
    ),
    "maclaurin_series": dict(
        name=r"Maclaurin Series",
        statement=r"\sin u=u-\frac{u^{3}}{3!}+\frac{u^{5}}{5!}-\cdots",
        symbols=[cap(r"$u$ is an angle in radians; $3!=6$.")],
        when=[cap(r"A function of a small quantity, needed to a few terms.")],
        why=[cap(r"The polynomial matches every derivative of $\sin$ at $0$.")],
    ),
    "exp_limit": dict(
        name=r"The Exponential Limit",
        statement=r"\lim_{k\to\infty}\Big(1+\frac{a}{k}\Big)^{k}=e^{a}",
        symbols=[cap(r"$a$ is fixed; $k$ grows without bound.")],
        when=[cap(r"A $k$-th power of something within $\frac{1}{k}$ of $1$.")],
        why=[cap(r"Its logarithm is $k\ln\big(1+\frac{a}{k}\big)\approx k\cdot\frac{a}{k}=a$.")],
    ),
    "dominated_convergence": dict(
        name=r"Limits Inside Integrals",
        statement=r"\lim_{k\to\infty}\int f_{k}\,dt=\int\lim_{k\to\infty}f_{k}\,dt\quad\text{if }|f_{k}|\le g",
        symbols=[cap(r"$f_{k}$ are the integrands; $g$ is one bound with finite area.")],
        when=[cap(r"A limit outside an integral that you want inside.")],
        why=[cap(r"The bound $g$ stops area escaping to infinity as $k$ grows.")],
    ),
}


# ---- Which cards are shown (from 2026-10-12)
# Beginner and Easy follow the Pure Year 1 syllabus, Medium the Further Pure syllabus (never
# named on screen). Hard (from 2026-10-22, user 2026-10-21) shows fewer cards: only rules
# beyond the syllabus (ADVANCED) get a card, a full one; a technique's first use gets a corner
# tag ("Using: ...") instead of a short card, and assumed rules and standard integrals nothing. A rule taught before the syllabus gets no card; techniques get a short
# card (name, statement, how it applies here); rules beyond the syllabus get the full card.
# A rule's later uses in the same video show a small corner tag instead of a card.
SILENT = {          # assumed known: no card and no tag; the step's caption carries the working
    "power_rule", "linearity", "constant_of_integration", "ftc", "log_laws", "exponent_laws",
    "absolute_value", "log_values", "exp_log_inverse", "exp_derivative", "ln_derivative",
    "quadratic_formula", "sin_cos_derivatives",
}
STANDARD = {"exp_integral", "reciprocal_integral", "sin_integral", "cos_integral", "sec2_integral"}
STANDARD_CARD_LEVELS = ("Beginner", "Easy")     # Medium viewers know the standard integrals
TAG_ONLY_LEVELS = ("Hard",)                     # techniques get a corner tag, not a short card
ADVANCED = {"laplace_transform", "nested_fixed_point", "arctan_integral", "average_value",
            "divisor_sum", "contour_shift", "gaussian_integral", "differentiation_under_integral",
            "analytic_continuation", "sech_cosine_transform", "swap_order", "one_minus_cos_integral",
            "catalan_constant", "log_cosine_series", "dilogarithm", "heaviside_step",
            "dominated_convergence"}     # always the full card


def card_kind(key, difficulty):
    """How a rule's first use in a video is shown: "full", "short" or None (no card)."""
    if key == ALGEBRA or key in SILENT:
        return None
    if key in ADVANCED:
        return "full"
    if key in STANDARD and difficulty not in STANDARD_CARD_LEVELS:
        return None
    if difficulty in TAG_ONLY_LEVELS:
        return None
    return "short"


def first_use_tag(key, difficulty):
    """True when a rule's first use shows a corner tag instead of a card (techniques in Hard)."""
    return (difficulty in TAG_ONLY_LEVELS and key != ALGEBRA and key not in SILENT
            and key not in STANDARD and card_kind(key, difficulty) is None)
