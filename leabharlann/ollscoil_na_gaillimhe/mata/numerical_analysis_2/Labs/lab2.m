%% MA378 (NA2) Lab2: piecewise linear interpolation

clear;

f = @(x)(sin(pi*x));

x0 = 0; xN=1; % Approximate f(x) in the interval [a,b]
N = 4; % The number of subintervals between a and b


h=(xN-x0)/N;

x = x0:h:xN;  % the points x(1), x(2), ..., x(n+1)

X = x0:1e-3:xN;    % X is a collection of points at which we'll
                 % evaluate f(x) and p(x) in order to plot them.
%%% Now evaluate the interpolant at each point X(i)
for i=1:length(X)
	L(i) = lspline(x,f(x), X(i));
end


%% Now plot the function and the interpolation.
subplot(2,1,1); 
plot(x,f(x), 'o', X, L, '-', X, f(X), 'MarkerSize', 8);
legend('y_i', 'L(x_i)', 'f(x)')
title('f(x) and L(x)');

%% And the error
subplot(2,1,2);
plot( X, f(X) - L,x,0,'o', 'MarkerSize', 8);
title('Error');

error=max(abs(f(X)-L));
fprintf('N=%4d, h=%8.2e, ||f-L||=%9.3e\n', N , h, error); 
%% 
error/h^2
%% 
clear;
x0 = 0; xN=1; % Approximate f(x) in the interval [a,b]
f = @(x)(sin(pi*x));
for i = 1:40
    N=i;
    
    h(i)=(xN-x0)/N;
    
    x = x0:h(i):xN;
    
    y = f(x);
    X = x0:1e-3:xN;

    for j=1:length(X)
        L(j) = lspline(x,f(x), X(j));
    end
    max_error = max(abs(f(X)-L));
    
    max_errors(i)=max_error;
    
    if max_error <= 1e-3
        break
    end
    
    C(i) = max_errors(i) / (h(i)^2)
    
end


%% sec
%% 
clear;
x0 = 0; xN=1; % Approximate f(x) in the interval [a,b]
f = @(x)(sin(pi*x));
for i = 1:80
    N=i;
    
    h=(xN-x0)/N;
    
    x = x0:h:xN;
    y = f(x);
    X = x0:1e-3:xN;

    for j=1:length(X)
        S(j) = spline(x,f(x), X(j));
    end
    
    
    
    max_error = max(abs(f(X)-S));
    max_errors(i)=max_error;
    C(i) = max_error / (h^4);

end
 %% 
clear;
x0 = 0; xN=1; % Approximate f(x) in the interval [a,b]
f = @(x)(sin(pi*x));
df = @(x)(pi*cos(pi*x));


for i = 1:40
    N=i;
    
    h(i)=(xN-x0)/N;
    
    x = x0:h(i):xN;
    
    X = x0:1e-3:xN;

    for j=1:length(X)
        S(j) = pchip_interp(x,f(x), df(x), X(j));
    end
    
    max_error = max(abs(f(X)-S));
    max_errors(i)=max_error;
   
    C(i) = max_error / (h(i)*h(i)*h(i)*h(i));
    
    
end















%% Now plot the function and the interpolation.
subplot(2,3,1); 
plot(x,f(x), 'o', X, S, '-', X, f(X));
legend('y_i', 'S(x_i)', 'f(x)')
title('f(x) and S(x)');
%% And the error
subplot(2,3,2);
plot( X, f(X) - S,x,0,'o', 'MarkerSize', 8);
title('Error');

error=max(abs(f(X)-S));
fprintf('N=%4d, h=%8.2e, ||f-L||=%9.3e\n', N , h, error); 