import "./PageHeader.css";

function PageHeader({ title, breadcrumb }) {
  return (
    <div className="page-header">

      <div className="left">
        {breadcrumb && (
          <div className="breadcrumb">
            {breadcrumb}
          </div>
        )}

        <h1>{title}</h1>
      </div>

      <div className="right">
        <button className="sync-btn">
            <img src="/img_PageHeader/synchronize-bold_.png" alt="sync" />
            <span>Synchroniser</span>
        </button>
      </div>

    </div>
  );
}

export default PageHeader;