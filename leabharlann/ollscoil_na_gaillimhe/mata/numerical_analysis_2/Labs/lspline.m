function L = lspline(x,f,X)
%%% function lspline for MA378 lab 2.
% Inputs: vectors x and y, both of length n
%         and a point X
% Output: A number L that is the piecewise linear
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
   %% Now compute L
   L = f(k-1)*(x(k)-X)/h + ...
      f(k)*(X - x(k-1))/h;
end

