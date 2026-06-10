%%Name: Cian Mac Liatháin ID: 11476078








%% Q3: cycles through possible values of n until error is <= 1e-6

a=-5; b= 5;
f = @(x)(exp(cos(x/2)));

for i = 1:50
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

%Error is 6.7092e-07 at n = 31 which is < 1e-6
%% Q6 calculates the Chebyshev points
a=-5; b= 5;
f = @(x)(1./(1+x.*x));
n = 38;
for i = 0:n;
    x = ((b-a)/2)*cos(((i+1/2)*pi)/(n+1))+(b+a)/2;
    points(i+1) = x;
end
%% Calculate the function values at the chebyshev x-values
%% create the interpolating polynomial and calculate the error
 y = f(points);
 X = a:1e-2:b;
 C = polyfit(points, y, n);

max_error = max(abs(f(X)-polyval(C,X)));
%%  Plots the function and interpolating polynomial
figure(1);
plot(points,y, 'o', X, f(X), X, polyval(C,X), '--')
legend('points', 'f', 'p_n');
title('f(x) and p_n(x)');
%% Shows the error
figure(2);
plot( X, f(X) -  polyval(C,X), '--')
title('Error: f(x)-p_n(x)');
%% We can see that the Chebyshev points are very 
%% good at minimising the error 
%% the error continues to decrease up to ~n= 38
%% however the error continues to grow for higher n at the tails of the graph
