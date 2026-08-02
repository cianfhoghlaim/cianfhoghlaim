import {withSpring} from "react-native-reanimated";

type SpringConfig = {
  response: number;
  dampingFraction: number;
};

export const calculateSpringConfig = ({
  response,
  dampingFraction,
}: SpringConfig) => {
  "worklet";

  const stiffness = ((2 * Math.PI) / response) ** 2;
  const damping = (4 * Math.PI * dampingFraction) / response;

  return {stiffness, damping};
};

/*
  response
    - The stiffness of the spring, defined as an approximate duration in seconds. 
    A value of zero requests an infinitely-stiff spring, suitable for driving interactive animations.

  dampingFraction
    - The amount of drag applied to the value being animated, 
    as a fraction of an estimate of amount needed to produce critical damping.
 */
export function spring(
  toValue: number,
  config: {response: number; dampingFraction: number} = {
    response: 0.15,
    dampingFraction: 0.825,
  },
) {
  "worklet";

  const {stiffness, damping} = calculateSpringConfig(config);

  return withSpring(toValue, {
    mass: 1,
    stiffness,
    damping,
  });
}

export const clamp = (num: number, min: number, max: number) => {
  "worklet";

  return Math.min(Math.max(num, min), max);
};
