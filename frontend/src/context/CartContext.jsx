import { useEffect, useState, useCallback } from "react";
import { CartContext } from "./CartContextObject";
import { getCart } from "../services/cartService";
import { useAuth } from "./useAuth";

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [cart, setCart] = useState(null);
  const [loaded, setLoaded] = useState(false);

  const refreshCart = useCallback(async () => {
    if (!user) {
      setCart(null);
      setLoaded(true);
      return;
    }
    try {
      const data = await getCart();
      setCart(data);
    } catch {
      setCart(null);
    } finally {
      setLoaded(true);
    }
  }, [user]);

  useEffect(() => {
    // Standard "fetch on mount / when dependency changes" pattern.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshCart();
  }, [refreshCart]);
  
  const itemCount = cart ? cart.items.reduce((sum, item) => sum + item.quantity, 0) : 0;

  return (
    <CartContext.Provider value={{ cart, itemCount, loaded, refreshCart, setCart }}>
      {children}
    </CartContext.Provider>
  );
}