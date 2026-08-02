import { useContext } from "react";
import { WishlistContext } from "./WishlistContextObject";

export function useWishlist() {
  return useContext(WishlistContext);
}