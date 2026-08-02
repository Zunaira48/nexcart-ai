import { useContext } from "react";
import { CartContext } from "./CartContextObject";

export function useCart() {
  return useContext(CartContext);
}