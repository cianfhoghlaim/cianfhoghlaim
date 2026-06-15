function S = pchip_interp(x,f,df,X)
%% Estimate for C for linear spline = 1.24
%% Estimate for C for natural cubic spline = 2.6e-1
%% Estimate for C for PCHIP = 
%%% function pchip for MA378 lab 2.
% Inputs: vectors x and y and df, of length n
%         and a point X
% Output: A number S that is the piecewise cubic hermmite
%           interpolant to (x_i, f_i) evaluated at the point X

N = length(x)-1; % Note - Matlab arrays are indexed from 1, not 0
h = (x(N+1)-x(1))/N;
%% First check that x(1) <= X <= x(N+1)
if (X < x(1) || X > x(N+1) )
   disp('Error - X is not in [x(0), x(N)]');
   return
else
   %% Find the interval [x(k), x(k+1)] containing X
   for i=2:N+1
      if ( (X >= x(i-1)) && (X <= x(i)) )
         k=i;
      end
   end
   %% Compute constants
   c0 = f(k-1);
   c1 = df(k-1);
   c2 = (3 /(h^2) ) * (f(k)-f(k-1)) - (1 / h) * (df(k) + 2 * (df(k-1)));
   c3 = (1 /(h^2)) * (df(k) + df(k-1)) - (2 / (h^3)) * (f(k)-f(k-1));
   
   %% Now compute S
   S = c0 + c1*(X - x(k-1)) + c2*(X - x(k-1)).^2 + c3*(X - x(k-1)).^3;

end

