import { useEffect, useState, useCallback } from "react";
import { WishlistContext } from "./WishlistContextObject";
import { getWishlist, addToWishlist, removeFromWishlist } from "../services/wishlistService";
import { useAuth } from "./useAuth";

export function WishlistProvider({ children }) {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loaded, setLoaded] = useState(false);

  const refreshWishlist = useCallback(async () => {
    if (!user) {
      setItems([]);
      setLoaded(true);
      return;
    }
    try {
      const data = await getWishlist();
      setItems(data);
    } catch {
      setItems([]);
    } finally {
      setLoaded(true);
    }
  }, [user]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    refreshWishlist();
  }, [refreshWishlist]);

  const productIds = items.map((item) => item.product.id);
  const isWishlisted = (productId) => productIds.includes(productId);

  const toggleWishlist = async (productId) => {
    if (isWishlisted(productId)) {
      await removeFromWishlist(productId);
    } else {
      await addToWishlist(productId);
    }
    await refreshWishlist();
  };

  return (
    <WishlistContext.Provider value={{ items, loaded, isWishlisted, toggleWishlist }}>
      {children}
    </WishlistContext.Provider>
  );
}