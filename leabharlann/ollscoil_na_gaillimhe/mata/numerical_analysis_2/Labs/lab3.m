%% MA378 - Numerical Analysis Lab 3
%Name: Cian Mac Liatháin
%ID: 11576078

% This program implemements the standard Newton-Cotes Quadrature method 
% to approximate the integral of f(x)=log(2*x) on [-1,1].
% By default, it ses the two-point method (i.e., Trapezium Rule).
% By uncommenting the defintions on n, x, and q, you can get it to use 
% the three-point (Simpson's) and four-point rules too.

%clear
% Example: approximate the integral of 
%f = @(x)log(2+x);
% from 
%a=-1;
%to 
%b=1;
% The correct answer  is
%Ans = 3*log(3)-2;

%% Newton Cotes Quadrature with n=1 
%n = 1;
%x = [-1,1];
%q = [1, 1]; % weights

%% Newton Cotes Quadrature with n=2
% n = 2;
% x = [-1,0,1];
% q = [1, 4, 1]/3; % weights

%% Newton Cotes Quadrature with n=3 
% n = 3;
% x = [-1, -1/3, 1/3, 1];
% q = [1, 3, 3, 1]/4; % weights

%% Newton Cotes Quadrature for any n > 1. Example: n=5
clear
% approximating the integral of
f = @(x)log(2+x);
% from 
a=-1;
%to 
b=1;
% The correct answer  is
Ans = 3*log(3)-2;

n=5;

% identify points
h=(b-a)/(n-1);
x = a:h:b;


% calculate coefficients of equations
coefficients= zeros(n,n);

fun=@(x,n) x.^(n-1);
fvalues=[];

for i = 1:n
    for j = 1:n
        coefficients(i,j)=x(j)^(i-1);
    end
    
    fvalues(i) = integral(@(x) x.^(i-1),a,b);
end

% solve for weights
q=transpose(linsolve(coefficients, transpose(fvalues)));
q
x
%Estimate and Error Calculator

Q = sum(q.*f(x));
QError = abs(Ans - Q);
fprintf('Q%d: Estimate = %8.6f, Error = %12.3e\n', n-1, Q, QError)

%% Guassian Quadrature (2-point)
clear
% approximating the integral of 
f = @(x)log(2+x);
% from 
a=-1;
%to 
b=1;
% The correct answer  is
Ans = 3*log(3)-2;

n=2;


% create system of equations
syms w0 w1 x0 x1

for i = 1:2*n
    if mod(i, 2) == 0
        fvalues(i) = 0; 
    else
        fvalues(i) = integral(@(x) x.^(i-1),a,b);
    end
    eqn(i) = w0*x0^(i-1)+w1*x1^(i-1)==fvalues(i);
end


% solve system of equations
[w0,w1,x0,x1] =solve([eqn(1),eqn(2),eqn(3), eqn(4)], [w0, w1, x0, x1]);

% identify weights and points
q = unique(round(w0, 4))
x = unique(round(x0,4))

%Estimate and Error Calculator

G = sum(q.*f(x));
GError = abs(Ans - G);
fprintf('G%d: Estimate = %8.6f, Error = %12.3e\n', n-1, G, GError)
%% Guassian Quadrature (3-point)
clear
% approximating the integral of
f = @(x)log(2+x);
% from 
a=-1;
%to 
b=1;
% The correct answer  is
Ans = 3*log(3)-2;

n=3;

% create system of equations

syms w0 w1 w2 x0 x1 x2

for i = 1:2*n
    if mod(i, 2) == 0
        fvalues(i) = 0; 
    else
        fvalues(i) = integral(@(x) x.^(i-1),a,b);
    end
    eqn(i) = w0*x0^(i-1)+w1*x1^(i-1)+w2*x2^(i-1)==fvalues(i);
end

% solve system of equations
[w0, w1, w2, x0, x1, x2] =solve([eqn(1),eqn(2),eqn(3), eqn(4), eqn(5), eqn(6)], [w0, w1, w2, x0, x1, x2]);

% identify weights and points
q = unique(round(w1,4));
q(n) = q(1);
x = unique(round(x1,4));
q
x
%Estimate and Error Calculator

G = sum(q.*f(x));
GError = abs(Ans - G);
fprintf('G%d: Estimate = %8.6f, Error = %12.3e\n', n-1, G, GError)
%% %% Guassian Quadrature (4-point)
clear
% approximating the integral of
f = @(x)log(2+x);
% from 
a=-1;
%to 
b=1;
% The correct answer  is
Ans = 3*log(3)-2;

n=4;

% create system of equations
syms w0 w1 w2 w3 x0 x1 x2 x3

for i = 1:2*n
    if mod(i, 2) == 0
        fvalues(i) = 0; 
    else
        fvalues(i) = integral(@(x) x.^(i-1),a,b);
    end
    eqn(i) = w0*x0^(i-1)+w1*x1^(i-1)+w2*x2^(i-1)+w3*x3^(i-1)==fvalues(i);
end

% solve system of equations
[w0, w1, w2, w3, x0, x1, x2, x3] =solve([eqn(1),eqn(2),eqn(3), eqn(4), eqn(5), eqn(6), eqn(7),eqn(8)], [w0, w1, w2, w3, x0, x1, x2, x3]);

% identify weights and points
q = unique(round(w0,4));
q(3)=q(2);
q(n)=q(1);
x = unique(round(x0,4));
q
x

%Estimate and Error Calculator

G = sum(q.*f(x));
GError = abs(Ans - G);
fprintf('G%d: Estimate = %8.6f, Error = %12.3e\n', n-1, G, GError)

%% We can see clearly that the Gaussian rules are more accurate than the 
% Newtown-Cotes rules at the same number of points
% G1 is more accurate than Q1 and Q2, G2 is more accurate than Q3
% G3 is more accurate than Q4
% Solving the non-linear equations can become more resource intensive
% for higher n, however.