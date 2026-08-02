import { useContext } from "react";
import { ThemeContext } from "./ThemeContextObject";

export function useTheme() {
  return useContext(ThemeContext);
}