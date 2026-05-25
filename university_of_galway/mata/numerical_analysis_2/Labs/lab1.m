%% MA378 : Numerical Analysis 1
% Lab 1, Q1: Experiment with polynomial interpolation



%% Define the function that we will interpolate 
f = @(x)(exp(cos(x/2)));

% The number of equally sized intervals. Also the
n = 2;    % degree of the interpolation polynomial.

a = -5; b = 5; % Approximate f(x) in the interval [a,b]=[-5,5].
h = (b-a)/n;   % h is the distance between interpolation points.

x = a:h:b;  % the points x(1), x(2), ..., x(n+1)
y = f(x);   % the points to interpolate

C = polyfit(x,y,n); % C is a vector containing the coefs of
                    % of the polynomial interpolant of f(x)
                   
X = a:1e-2:b;   % X is a collection of points at which we will
                % evaluate f(x) and p(x) in order to plot them.
%% Now plot the function and the interpolation.
figure(1);
plot(x,y, 'o', X, f(X), X, polyval(C,X), '--')
legend('points', 'f', 'p_n');
title('f(x) and p_n(x)');
%% And the error
figure(2);
plot( X, f(X) -  polyval(C,X), '--')
title('Error: f(x)-p_n(x)');
%% Q2:

n_2 = 2;
h_2 = (b-a)/5;

x_2 = a:h_2:b;
y_2=f(x_2);
C_2 = polyfit(x_2,y_2,n_2);
%% 
figure(22);
plot(x_2, y_2, 'o',X,f(X), X, polyval(C_2,X), '--')
legend('points','f','p_n');
title('f(x) and p_n(x)');
%%
figure(23);
plot(X, f(X) - polyval(C_2, X), '--');
title('Error: f(x-p_n(x)');
%% Q3:

a=-5; b= 5;
f = @(x)(exp(cos(x/2)));

for i = 1:31
    n=i;
    h = (b-a)/n;
    x = a:h:b;
    y = f(x);
    X = a:0.01:b;
    C = polyfit(x, y, n);


    max_error = [max(abs(f(X)-polyval(C,X)))];
    max_errors(i)=max_error;
    if max_error <= 1e-6
        break
    end
    
end

%Error is 6.7092e-07 at n = 31
%% Q4
a=-5; b= 5;
f = @(x)(1./(1+x.*x));
for i = 1:60
    n=i;
    h(i) = (b-a)/n;
    x = a:h(i):b;
    y = f(x)
    X = a:0.01:b;
    C = polyfit(x, y, n)

    error = f(X)-polyval(C,X)
    
    max_error = [max(abs(f(X)-polyval(C,X)))];
    max_errors(i)=max_error
    
end
%% Q5
%% Define the function that we will interpolate 
f = @(x)(1./(1+x.*x));


n=18;
a = -5; b = 5; 

x = [0,0.9,1.6,2.4,3.15,3.7,4.3,4.7,4.9,5];
x = union(-x,x);

y = f(x);   % the points to interpolate

C = polyfit(x,y,n); % C is a vector containing the coefs of
                    % of the polynomial interpolant of f(x)
                   
X = a:1e-2:b;   % X is a collection of points at which we will
                % evaluate f(x) and p(x) in order to plot them.
                
%% 
figure(1);
plot(x,y, 'o', X, f(X), X, polyval(C,X), '--')
legend('points', 'f', 'p_n');
title('f(x) and p_n(x)');
%% 
figure(2);
plot( X, f(X) -  polyval(C,X), '--')
title('Error: f(x)-p_n(x)');

%% Q6
a=-5; b= 5;
f = @(x)(1./(1+x.*x));
n=30;
for i = 1:30;
    x = ((b-a)/2)*cos(((i+1/2)*pi)/(n+1))+(b+a)/2;
    points(i) = x;
end
%% 
 y = f(points);
 X = a:1e-2:b;
 C = polyfit(points, y, n);

error = f(X)-polyval(C,X)
    
max_error = max(error);
max_errors(i)=max_error;
%% 
figure(1);
plot(points,y, 'o', X, f(X), X, polyval(C,X), '--')
legend('points', 'f', 'p_n');
title('f(x) and p_n(x)');
%% 
figure(2);
plot( X, f(X) -  polyval(C,X), '--')
title('Error: f(x)-p_n(x)');
